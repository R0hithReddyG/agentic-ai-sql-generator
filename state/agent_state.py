from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    IDLE = "idle"
    INTENT_ANALYSIS = "intent_analysis"
    SCHEMA_DISCOVERY = "schema_discovery"
    PLANNING = "planning"
    SQL_GENERATION = "sql_generation"
    VALIDATION = "validation"
    EXECUTION = "execution"
    ERROR_RECOVERY = "error_recovery"
    RESULT_VERIFICATION = "result_verification"
    ANSWER_SYNTHESIS = "answer_synthesis"
    CLARIFICATION_NEEDED = "clarification_needed"
    COMPLETED = "completed"
    FAILED = "failed"


class IntentAnalysis(BaseModel):
    original_question: str
    entities: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)
    filters: list[str] = Field(default_factory=list)
    aggregations: list[str] = Field(default_factory=list)
    time_constraints: list[str] = Field(default_factory=list)
    join_hints: list[str] = Field(default_factory=list)
    is_ambiguous: bool = False
    ambiguity_reasons: list[str] = Field(default_factory=list)
    clarification_questions: list[str] = Field(default_factory=list)


class SubPlan(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str
    tables_involved: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    sql: Optional[str] = None
    result_summary: Optional[str] = None
    status: str = "pending"


class ExecutionPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    strategy: str = "single_query"
    sub_plans: list[SubPlan] = Field(default_factory=list)
    reasoning: str = ""
    estimated_complexity: str = "low"


class ToolCallRecord(BaseModel):
    call_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    tool_name: str
    input_params: dict[str, Any] = Field(default_factory=dict)
    output: Optional[Any] = None
    success: bool = True
    error_message: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ErrorRecord(BaseModel):
    error_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    phase: str
    error_type: str
    message: str
    sql_attempted: Optional[str] = None
    root_cause_analysis: Optional[str] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class CorrectionAttempt(BaseModel):
    attempt_number: int
    original_sql: Optional[str] = None
    corrected_sql: Optional[str] = None
    error_addressed: str
    strategy: str
    success: bool = False
    details: Optional[str] = None


class ValidationCheck(BaseModel):
    check_name: str
    passed: bool
    details: Optional[str] = None


class AgentState(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: AgentStatus = AgentStatus.IDLE
    original_question: str = ""
    intent: Optional[IntentAnalysis] = None
    schema_context: dict[str, Any] = Field(default_factory=dict)
    execution_plan: Optional[ExecutionPlan] = None
    current_sql: Optional[str] = None
    generated_sql_history: list[str] = Field(default_factory=list)
    query_results: Optional[list[dict[str, Any]]] = None
    result_columns: list[str] = Field(default_factory=list)
    row_count: int = 0
    tool_call_log: list[ToolCallRecord] = Field(default_factory=list)
    errors: list[ErrorRecord] = Field(default_factory=list)
    correction_attempts: list[CorrectionAttempt] = Field(default_factory=list)
    validation_checks: list[ValidationCheck] = Field(default_factory=list)
    max_retries: int = 3
    current_retry: int = 0
    final_answer: Optional[str] = None
    synthesized_response: Optional[dict[str, Any]] = None
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def add_tool_call(self, record: ToolCallRecord) -> None:
        self.tool_call_log.append(record)
        self.touch()

    def add_error(self, error: ErrorRecord) -> None:
        self.errors.append(error)
        self.touch()

    def add_correction(self, correction: CorrectionAttempt) -> None:
        self.correction_attempts.append(correction)
        self.touch()

    def can_retry(self) -> bool:
        return self.current_retry < self.max_retries

    def increment_retry(self) -> None:
        self.current_retry += 1
        self.touch()
