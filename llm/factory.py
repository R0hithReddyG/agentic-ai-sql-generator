from __future__ import annotations

from typing import Optional

from config.settings import get_settings
from llm.base import LLMProvider

_provider: Optional[LLMProvider] = None


def get_llm_provider() -> LLMProvider:
    global _provider
    if _provider is not None:
        return _provider

    settings = get_settings()
    provider_name = settings.llm_provider.lower()

    if provider_name == "openai":
        from llm.openai_provider import OpenAIProvider

        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using openai provider")
        _provider = OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            base_url=settings.openai_base_url,
        )
    elif provider_name == "mock":
        from llm.mock_provider import MockLLMProvider

        _provider = MockLLMProvider()
    else:
        from llm.mock_provider import MockLLMProvider

        _provider = MockLLMProvider()

    return _provider


def set_llm_provider(provider: LLMProvider) -> None:
    global _provider
    _provider = provider
