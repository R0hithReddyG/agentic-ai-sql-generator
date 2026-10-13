from __future__ import annotations

import time
from typing import Any, Optional

from database.engine import execute_read_only
from database.safety import validate_sql_safety
from tools.base_tool import ToolOutput
from tools.registry import ToolRegistry


def execute_query(sql: str, params: Optional[dict[str, Any]] = None) -> ToolOutput:
    start = time.time()
    try:
        is_safe, reason = validate_sql_safety(sql)
        if not is_safe:
            return ToolOutput(
                tool_name="execute_query",
                success=False,
                error=f"Safety violation: {reason}",
                duration_ms=(time.time() - start) * 1000,
            )

        rows = execute_read_only(sql, params)
        columns = list(rows[0].keys()) if rows else []
        return ToolOutput(
            tool_name="execute_query",
            success=True,
            data={
                "rows": rows,
                "columns": columns,
                "row_count": len(rows),
            },
            duration_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        return ToolOutput(
            tool_name="execute_query",
            success=False,
            error=str(e),
            duration_ms=(time.time() - start) * 1000,
        )


def validate_sql_syntax(sql: str) -> ToolOutput:
    start = time.time()
    try:
        import sqlglot
        from config.settings import get_settings

        dialect = get_settings().dialect
        parsed = sqlglot.parse(sql, read=dialect)
        errors = []
        for expr in parsed:
            if expr is None:
                errors.append("Empty expression found")

        is_safe, safety_reason = validate_sql_safety(sql)
        if not is_safe:
            errors.append(f"Safety: {safety_reason}")

        return ToolOutput(
            tool_name="validate_sql_syntax",
            success=len(errors) == 0,
            data={"parsed": True, "errors": errors},
            error="; ".join(errors) if errors else None,
            duration_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        return ToolOutput(
            tool_name="validate_sql_syntax",
            success=False,
            error=str(e),
            duration_ms=(time.time() - start) * 1000,
        )


def explain_query(sql: str) -> ToolOutput:
    start = time.time()
    try:
        is_safe, reason = validate_sql_safety(sql)
        if not is_safe:
            return ToolOutput(
                tool_name="explain_query",
                success=False,
                error=f"Safety violation: {reason}",
                duration_ms=(time.time() - start) * 1000,
            )

        from database.engine import get_engine
        from sqlalchemy import text

        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(f"EXPLAIN QUERY PLAN {sql}"))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result]
        return ToolOutput(
            tool_name="explain_query",
            success=True,
            data={"plan": rows},
            duration_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        return ToolOutput(
            tool_name="explain_query",
            success=False,
            error=str(e),
            duration_ms=(time.time() - start) * 1000,
        )


registry = ToolRegistry()
registry.register("execute_query", execute_query)
registry.register("validate_sql_syntax", validate_sql_syntax)
registry.register("explain_query", explain_query)
