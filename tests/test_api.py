import pytest
from services.query_service import QueryRequest, process_query
from llm.mock_provider import MockLLMProvider
from llm.factory import set_llm_provider
from database.seed import seed_database


@pytest.fixture(autouse=True)
def setup():
    set_llm_provider(MockLLMProvider())
    seed_database()


def test_process_query_returns_response():
    request = QueryRequest(question="How many customers exist?")
    response = process_query(request)
    assert response.session_id != ""
    assert response.status in ("completed", "failed", "clarification_needed")


def test_process_query_includes_trace():
    request = QueryRequest(question="List departments")
    response = process_query(request)
    assert len(response.trace) > 0


def test_empty_question():
    request = QueryRequest(question="   ")
    response = process_query(request)
    assert response.status in ("failed", "completed")
