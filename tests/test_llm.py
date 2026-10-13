import pytest
from llm.mock_provider import MockLLMProvider
from llm.base import LLMResponse


def test_mock_provider_returns_response():
    provider = MockLLMProvider()
    response = provider.generate(prompt="test", system_prompt="system")
    assert isinstance(response, LLMResponse)
    assert response.content != ""


def test_mock_provider_name():
    provider = MockLLMProvider()
    assert provider.name() == "mock"


def test_mock_sql_generation():
    provider = MockLLMProvider()
    response = provider.generate(prompt="generate sql for this question")
    assert "sql" in response.content.lower() or "SELECT" in response.content.upper()


def test_mock_intent_analysis():
    provider = MockLLMProvider()
    response = provider.generate(prompt="analyze the intent of this question")
    assert "entities" in response.content
