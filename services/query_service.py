from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel

from agents.orchestrator import OrchestratorAgent
from state.agent_state import AgentState


class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    session_id: str
    status: str
    answer: Optional[str] = None
    sql: Optional[str] = None
    row_count: int = 0
    results: Optional[list[dict[str, Any]]] = None
    trace: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    corrections: list[dict[str, Any]] = []
    synthesized_response: Optional[dict[str, Any]] = None


def process_query(request: QueryRequest) -> QueryResponse:
    orchestrator = OrchestratorAgent()
    state = orchestrator.process(
        question=request.question,
        session_id=request.session_id,
    )
    return _state_to_response(state)


def _state_to_response(state: AgentState) -> QueryResponse:
    trace = [
        {
            "tool_name": tc.tool_name,
            "success": tc.success,
            "duration_ms": tc.duration_ms,
            "error": tc.error_message,
        }
        for tc in state.tool_call_log
    ]
    errors = [
        {
            "phase": e.phase,
            "error_type": e.error_type,
            "message": e.message,
        }
        for e in state.errors
    ]
    corrections = [
        {
            "attempt_number": c.attempt_number,
            "original_sql": c.original_sql,
            "corrected_sql": c.corrected_sql,
            "strategy": c.strategy,
            "success": c.success,
        }
        for c in state.correction_attempts
    ]

    return QueryResponse(
        session_id=state.session_id,
        status=state.status.value,
        answer=state.final_answer,
        sql=state.current_sql,
        row_count=state.row_count,
        results=state.query_results,
        trace=trace,
        errors=errors,
        corrections=corrections,
        synthesized_response=state.synthesized_response,
    )
