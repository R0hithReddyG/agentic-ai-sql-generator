from __future__ import annotations

import time
from typing import Any

from sqlalchemy import inspect, text

from database.engine import get_engine
from tools.base_tool import ToolOutput
from tools.registry import ToolRegistry


def list_tables() -> ToolOutput:
    start = time.time()
    try:
        engine = get_engine()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return ToolOutput(
            tool_name="list_tables",
            success=True,
            data={"tables": tables},
            duration_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        return ToolOutput(
            tool_name="list_tables",
            success=False,
            error=str(e),
            duration_ms=(time.time() - start) * 1000,
        )


def describe_table(table_name: str) -> ToolOutput:
    start = time.time()
    try:
        engine = get_engine()
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        pk = inspector.get_pk_constraint(table_name)
        fks = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)

        col_info = []
        for col in columns:
            col_info.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
                "default": str(col["default"]) if col.get("default") else None,
            })

        fk_info = []
        for fk in fks:
            fk_info.append({
                "constrained_columns": fk["constrained_columns"],
                "referred_table": fk["referred_table"],
                "referred_columns": fk["referred_columns"],
            })

        idx_info = []
        for idx in indexes:
            idx_info.append({
                "name": idx["name"],
                "columns": idx["column_names"],
                "unique": idx["unique"],
            })

        return ToolOutput(
            tool_name="describe_table",
            success=True,
            data={
                "table": table_name,
                "columns": col_info,
                "primary_key": pk,
                "foreign_keys": fk_info,
                "indexes": idx_info,
            },
            duration_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        return ToolOutput(
            tool_name="describe_table",
            success=False,
            error=str(e),
            duration_ms=(time.time() - start) * 1000,
        )


def get_sample_data(table_name: str, limit: int = 5) -> ToolOutput:
    start = time.time()
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT :limit"), {"limit": limit})
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result]
        return ToolOutput(
            tool_name="get_sample_data",
            success=True,
            data={"columns": columns, "rows": rows},
            duration_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        return ToolOutput(
            tool_name="get_sample_data",
            success=False,
            error=str(e),
            duration_ms=(time.time() - start) * 1000,
        )


def get_full_schema() -> ToolOutput:
    start = time.time()
    try:
        tables_result = list_tables()
        if not tables_result.success or not tables_result.data:
            return tables_result

        schema: dict[str, Any] = {}
        for tbl in tables_result.data["tables"]:
            desc = describe_table(tbl)
            if desc.success and desc.data:
                schema[tbl] = desc.data

        return ToolOutput(
            tool_name="get_full_schema",
            success=True,
            data=schema,
            duration_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        return ToolOutput(
            tool_name="get_full_schema",
            success=False,
            error=str(e),
            duration_ms=(time.time() - start) * 1000,
        )


registry = ToolRegistry()
registry.register("list_tables", list_tables)
registry.register("describe_table", describe_table)
registry.register("get_sample_data", get_sample_data)
registry.register("get_full_schema", get_full_schema)
