from __future__ import annotations

import json
from typing import Any

from llm.base import LLMProvider
from tools.execution_tools import validate_sql_syntax
from state.agent_state import ValidationCheck

VALIDATOR_SYSTEM_PROMPT = """You are a SQL validator. Check if the generated SQL is correct given the schema.

Validate:
1. All referenced tables exist in the schema
2. All referenced columns exist in their respective tables
3. JOIN conditions are valid
4. Aggregations have appropriate GROUP BY clauses
5. No ambiguous column references

Return JSON: {"is_valid": bool, "issues": ["list of issues"], "corrected_sql": "optional corrected SQL or null"}
"""


def validate_sql(
    sql: str,
    schema_context: dict[str, Any],
    llm: LLMProvider,
) -> tuple[bool, list[ValidationCheck], str | None]:
    checks: list[ValidationCheck] = []

    syntax_result = validate_sql_syntax(sql)
    checks.append(ValidationCheck(
        check_name="syntax_validation",
        passed=syntax_result.success,
        details=syntax_result.error,
    ))

    if not syntax_result.success:
        return False, checks, None

    prompt = f"""Validate this SQL against the schema:

SQL: {sql}

Schema:
{json.dumps(schema_context, indent=2, default=str)}

Return only valid JSON."""

    response = llm.generate(prompt=prompt, system_prompt=VALIDATOR_SYSTEM_PROMPT)

    try:
        data = json.loads(response.content)
    except json.JSONDecodeError:
        data = {"is_valid": True, "issues": [], "corrected_sql": None}

    is_valid = data.get("is_valid", True)
    issues = data.get("issues", [])
    corrected_sql = data.get("corrected_sql")

    checks.append(ValidationCheck(
        check_name="semantic_validation",
        passed=is_valid,
        details="; ".join(issues) if issues else None,
    ))

    return is_valid, checks, corrected_sql
