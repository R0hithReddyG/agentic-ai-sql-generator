from __future__ import annotations

from typing import Any, Optional

from tools.execution_tools import execute_query
from tools.base_tool import ToolOutput


def execute_sql(sql: str, params: Optional[dict[str, Any]] = None) -> ToolOutput:
    return execute_query(sql, params)
