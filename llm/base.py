from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel


class LLMResponse(BaseModel):
    content: str
    model: str = ""
    tokens_used: int = 0
    raw_response: Optional[Any] = None


class LLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> LLMResponse:
        pass

    @abstractmethod
    def name(self) -> str:
        pass
