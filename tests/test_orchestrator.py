import pytest
from agents.orchestrator import OrchestratorAgent
from llm.mock_provider import MockLLMProvider
from llm.factory import set_llm_provider
from state.agent_state import AgentStatus
from database.seed import seed_database


@pytest.fixture(autouse=True)
def setup_db():
    set_llm_provider(MockLLMProvider())
    seed_database()


def test_orchestrator_basic_query():
    orchestrator = OrchestratorAgent(llm=MockLLMProvider())
    state = orchestrator.process("How many employees are there?")
    assert state.status in (AgentStatus.COMPLETED, AgentStatus.FAILED)
    assert state.original_question == "How many employees are there?"
    assert len(state.tool_call_log) > 0


def test_orchestrator_records_tool_calls():
    orchestrator = OrchestratorAgent(llm=MockLLMProvider())
    state = orchestrator.process("List all departments")
    tool_names = [tc.tool_name for tc in state.tool_call_log]
    assert "analyze_intent" in tool_names
    assert "discover_schema" in tool_names


def test_orchestrator_has_schema_context():
    orchestrator = OrchestratorAgent(llm=MockLLMProvider())
    state = orchestrator.process("What is the average salary?")
    assert state.schema_context is not None


def test_orchestrator_generates_sql():
    orchestrator = OrchestratorAgent(llm=MockLLMProvider())
    state = orchestrator.process("Count all orders")
    assert len(state.generated_sql_history) > 0
