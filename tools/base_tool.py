from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel


class ToolInput(BaseModel):
    tool_name: str
    parameters: dict[str, Any] = {}


class ToolOutput(BaseModel):
    tool_name: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0


class BaseTool(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolOutput:
        pass

    @abstractmethod
    def description(self) -> str:
        pass
