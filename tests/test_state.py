import pytest
from state.agent_state import AgentState, AgentStatus, IntentAnalysis


def test_agent_state_creation():
    state = AgentState(original_question="test")
    assert state.status == AgentStatus.IDLE
    assert state.original_question == "test"
    assert state.current_retry == 0
    assert state.can_retry() is True


def test_agent_state_retry_limit():
    state = AgentState(original_question="test", max_retries=2)
    state.increment_retry()
    state.increment_retry()
    assert state.can_retry() is False


def test_intent_analysis():
    intent = IntentAnalysis(
        original_question="How many employees?",
        entities=["employees"],
        aggregations=["COUNT"],
        is_ambiguous=False,
    )
    assert intent.entities == ["employees"]
    assert intent.is_ambiguous is False


def test_agent_state_tool_call_log():
    from state.agent_state import ToolCallRecord
    state = AgentState(original_question="test")
    record = ToolCallRecord(tool_name="test_tool", input_params={"a": 1})
    state.add_tool_call(record)
    assert len(state.tool_call_log) == 1
    assert state.tool_call_log[0].tool_name == "test_tool"
