from __future__ import annotations

import json
from typing import Any

from llm.base import LLMProvider
from state.agent_state import AgentState

GENERATOR_SYSTEM_PROMPT = """You are a SQL generation engine. Generate dialect-specific SQL based on the schema and intent provided.

Rules:
1. Use ONLY tables and columns that exist in the provided schema
2. Generate valid SQL for the specified dialect
3. Include appropriate JOINs based on foreign key relationships
4. Apply filters, aggregations, and grouping as indicated by the intent
5. Never generate DDL or DML statements
6. Return ONLY valid JSON: {"sql": "your SQL query here"}
"""


def generate_sql(
    question: str,
    schema_context: dict[str, Any],
    intent: dict[str, Any],
    plan: dict[str, Any],
    dialect: str,
    llm: LLMProvider,
    error_context: str = "",
) -> str:
    prompt = f"""Generate SQL for the following:

Question: {question}
Dialect: {dialect}

Schema:
{json.dumps(schema_context, indent=2, default=str)}

Intent:
{json.dumps(intent, indent=2, default=str)}

Plan:
{json.dumps(plan, indent=2, default=str)}
"""
    if error_context:
        prompt += f"\n\nPrevious error to fix:\n{error_context}"

    prompt += "\n\nReturn only valid JSON with a 'sql' key."

    response = llm.generate(prompt=prompt, system_prompt=GENERATOR_SYSTEM_PROMPT)

    try:
        data = json.loads(response.content)
        return data.get("sql", "SELECT 1")
    except json.JSONDecodeError:
        sql_text = response.content.strip()
        if sql_text.upper().startswith("SELECT") or sql_text.upper().startswith("WITH"):
            return sql_text.rstrip(";") + ";" if not sql_text.endswith(";") else sql_text
        return "SELECT 1;"
