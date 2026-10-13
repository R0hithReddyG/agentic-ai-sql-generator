from __future__ import annotations

import logging
from typing import Any, Optional

from agents.schema_agent import analyze_intent
from agents.planner_agent import discover_schema
from agents.generator_agent import generate_sql
from agents.validator_agent import validate_sql
from agents.executor_agent import execute_sql
from agents.verifier_agent import verify_results
from agents.error_recovery import recover_from_error
from agents.synthesizer import synthesize_answer
from config.settings import get_settings
from llm.base import LLMProvider
from llm.factory import get_llm_provider
from plan.decomposer import create_execution_plan
from state.agent_state import (
    AgentState,
    AgentStatus,
    CorrectionAttempt,
    ErrorRecord,
    ToolCallRecord,
)

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    def __init__(
        self,
        llm: Optional[LLMProvider] = None,
        max_retries: int = 3,
    ) -> None:
        self.llm = llm or get_llm_provider()
        self.max_retries = max_retries

    def process(self, question: str, session_id: Optional[str] = None) -> AgentState:
        state = AgentState(
            original_question=question,
            max_retries=self.max_retries,
        )
        if session_id:
            state.session_id = session_id

        logger.info(f"[{state.session_id}] Processing: {question}")

        state.status = AgentStatus.INTENT_ANALYSIS
        state.touch()
        self._run_intent_analysis(state)

        if state.intent and state.intent.is_ambiguous:
            state.status = AgentStatus.CLARIFICATION_NEEDED
            state.final_answer = "Clarification needed: " + "; ".join(
                state.intent.clarification_questions
            )
            state.touch()
            return state

        state.status = AgentStatus.SCHEMA_DISCOVERY
        state.touch()
        self._run_schema_discovery(state)

        state.status = AgentStatus.PLANNING
        state.touch()
        self._run_planning(state)

        state.status = AgentStatus.SQL_GENERATION
        state.touch()
        self._run_sql_generation_loop(state)

        if state.status == AgentStatus.FAILED:
            return state

        state.status = AgentStatus.ANSWER_SYNTHESIS
        state.touch()
        self._run_synthesis(state)

        state.status = AgentStatus.COMPLETED
        state.touch()
        return state

    def _run_intent_analysis(self, state: AgentState) -> None:
        try:
            intent = analyze_intent(state.original_question, self.llm)
            state.intent = intent
            state.add_tool_call(ToolCallRecord(
                tool_name="analyze_intent",
                input_params={"question": state.original_question},
                output=intent.model_dump(),
                success=True,
            ))
        except Exception as e:
            state.add_error(ErrorRecord(
                phase="intent_analysis",
                error_type="exception",
                message=str(e),
            ))
            state.intent = None

    def _run_schema_discovery(self, state: AgentState) -> None:
        try:
            schema = discover_schema(state)
            state.schema_context = schema
            state.add_tool_call(ToolCallRecord(
                tool_name="discover_schema",
                input_params={},
                output={"tables_found": len(schema)},
                success=True,
            ))
        except Exception as e:
            state.add_error(ErrorRecord(
                phase="schema_discovery",
                error_type="exception",
                message=str(e),
            ))

    def _run_planning(self, state: AgentState) -> None:
        try:
            intent_dict = state.intent.model_dump() if state.intent else {}
            plan = create_execution_plan(
                question=state.original_question,
                schema_context=state.schema_context,
                intent=intent_dict,
                llm=self.llm,
            )
            state.execution_plan = plan
            state.add_tool_call(ToolCallRecord(
                tool_name="create_plan",
                input_params={"question": state.original_question},
                output=plan.model_dump(),
                success=True,
            ))
        except Exception as e:
            state.add_error(ErrorRecord(
                phase="planning",
                error_type="exception",
                message=str(e),
            ))

    def _run_sql_generation_loop(self, state: AgentState) -> None:
        settings = get_settings()
        error_context = ""

        while state.can_retry():
            state.status = AgentStatus.SQL_GENERATION
            state.touch()

            try:
                intent_dict = state.intent.model_dump() if state.intent else {}
                plan_dict = state.execution_plan.model_dump() if state.execution_plan else {}

                sql = generate_sql(
                    question=state.original_question,
                    schema_context=state.schema_context,
                    intent=intent_dict,
                    plan=plan_dict,
                    dialect=settings.dialect,
                    llm=self.llm,
                    error_context=error_context,
                )
                state.current_sql = sql
                state.generated_sql_history.append(sql)

                state.add_tool_call(ToolCallRecord(
                    tool_name="generate_sql",
                    input_params={"question": state.original_question},
                    output={"sql": sql},
                    success=True,
                ))
            except Exception as e:
                state.add_error(ErrorRecord(
                    phase="sql_generation",
                    error_type="generation_error",
                    message=str(e),
                    sql_attempted=state.current_sql,
                ))
                state.increment_retry()
                continue

            state.status = AgentStatus.VALIDATION
            state.touch()

            try:
                is_valid, checks, corrected_sql = validate_sql(
                    sql=sql,
                    schema_context=state.schema_context,
                    llm=self.llm,
                )
                state.validation_checks.extend(checks)

                if corrected_sql and not is_valid:
                    sql = corrected_sql
                    state.current_sql = sql

                state.add_tool_call(ToolCallRecord(
                    tool_name="validate_sql",
                    input_params={"sql": sql},
                    output={"is_valid": is_valid, "checks": [c.model_dump() for c in checks]},
                    success=is_valid,
                ))

                if not is_valid and not corrected_sql:
                    error_context = f"Validation failed: {[c.details for c in checks if not c.passed]}"
                    state.increment_retry()
                    continue
            except Exception as e:
                state.add_error(ErrorRecord(
                    phase="validation",
                    error_type="exception",
                    message=str(e),
                ))
                state.increment_retry()
                continue

            state.status = AgentStatus.EXECUTION
            state.touch()

            exec_result = execute_sql(sql)
            state.add_tool_call(ToolCallRecord(
                tool_name="execute_sql",
                input_params={"sql": sql},
                output=exec_result.data,
                success=exec_result.success,
                error_message=exec_result.error,
                duration_ms=exec_result.duration_ms,
            ))

            if not exec_result.success:
                state.status = AgentStatus.ERROR_RECOVERY
                state.touch()
                state.add_error(ErrorRecord(
                    phase="execution",
                    error_type="execution_error",
                    message=exec_result.error or "Unknown execution error",
                    sql_attempted=sql,
                ))

                try:
                    corrected_sql, root_cause = recover_from_error(
                        question=state.original_question,
                        failed_sql=sql,
                        error_message=exec_result.error or "",
                        schema_context=state.schema_context,
                        llm=self.llm,
                    )
                    state.add_correction(CorrectionAttempt(
                        attempt_number=state.current_retry + 1,
                        original_sql=sql,
                        corrected_sql=corrected_sql,
                        error_addressed=exec_result.error or "",
                        strategy="llm_error_recovery",
                        details=root_cause,
                    ))
                    error_context = f"Previous error: {exec_result.error}. Root cause: {root_cause}"
                except Exception as e:
                    error_context = f"Recovery failed: {e}"

                state.increment_retry()
                continue

            if exec_result.data:
                state.query_results = exec_result.data.get("rows", [])
                state.result_columns = exec_result.data.get("columns", [])
                state.row_count = exec_result.data.get("row_count", 0)

            state.status = AgentStatus.RESULT_VERIFICATION
            state.touch()

            try:
                is_verified, ver_checks, confidence = verify_results(
                    question=state.original_question,
                    sql=sql,
                    rows=state.query_results or [],
                    llm=self.llm,
                )
                state.validation_checks.extend(ver_checks)

                if is_verified or confidence >= 0.5:
                    return
                else:
                    error_context = f"Verification failed: {[c.details for c in ver_checks if not c.passed]}"
                    state.increment_retry()
                    continue
            except Exception as e:
                state.add_error(ErrorRecord(
                    phase="verification",
                    error_type="exception",
                    message=str(e),
                ))
                return

        state.status = AgentStatus.FAILED
        state.final_answer = (
            f"Failed after {state.max_retries} attempts. "
            f"Errors: {[e.message for e in state.errors[-3:]]}"
        )
        state.touch()

    def _run_synthesis(self, state: AgentState) -> None:
        if not state.query_results:
            state.synthesized_response = {
                "answer": "Query executed successfully but returned no results.",
                "confidence": 0.8,
                "caveats": [],
                "sql_executed": state.current_sql,
                "row_count": 0,
            }
            state.final_answer = state.synthesized_response["answer"]
            return

        try:
            response = synthesize_answer(
                question=state.original_question,
                sql=state.current_sql or "",
                rows=state.query_results,
                llm=self.llm,
            )
            state.synthesized_response = response
            state.final_answer = response.get("answer", "Answer generated.")
        except Exception as e:
            state.add_error(ErrorRecord(
                phase="synthesis",
                error_type="exception",
                message=str(e),
            ))
            state.final_answer = f"Query returned {state.row_count} results."
            state.synthesized_response = {
                "answer": state.final_answer,
                "confidence": 0.5,
                "caveats": ["Synthesis failed"],
                "sql_executed": state.current_sql,
                "row_count": state.row_count,
            }
