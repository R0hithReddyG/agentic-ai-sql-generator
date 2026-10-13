from __future__ import annotations

from typing import Any

from tools.schema_tools import get_full_schema, list_tables, describe_table, get_sample_data
from state.agent_state import AgentState


def discover_schema(state: AgentState) -> dict[str, Any]:
    schema_result = get_full_schema()
    if schema_result.success and schema_result.data:
        return schema_result.data

    tables_result = list_tables()
    if not tables_result.success or not tables_result.data:
        return {}

    schema: dict[str, Any] = {}
    for tbl in tables_result.data.get("tables", []):
        desc = describe_table(tbl)
        if desc.success and desc.data:
            schema[tbl] = desc.data

    return schema
