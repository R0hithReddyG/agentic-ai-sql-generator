from __future__ import annotations

import json
from typing import Any

from llm.base import LLMProvider

ERROR_RECOVERY_SYSTEM_PROMPT = """You are a SQL error recovery agent. Analyze the error and produce a corrected SQL query.

Given:
- The original question
- The failed SQL
- The error message
- The database schema

Diagnose the root cause and return a corrected SQL query.

Return JSON: {"root_cause": "explanation", "corrected_sql": "fixed SQL", "explanation": "what was wrong"}
"""


def recover_from_error(
    question: str,
    failed_sql: str,
    error_message: str,
    schema_context: dict[str, Any],
    llm: LLMProvider,
) -> tuple[str, str]:
    prompt = f"""Fix this SQL error:

Question: {question}
Failed SQL: {failed_sql}
Error: {error_message}

Schema:
{json.dumps(schema_context, indent=2, default=str)}

Return only valid JSON with root_cause, corrected_sql, and explanation keys."""

    response = llm.generate(prompt=prompt, system_prompt=ERROR_RECOVERY_SYSTEM_PROMPT)

    try:
        data = json.loads(response.content)
        return data.get("corrected_sql", failed_sql), data.get("root_cause", "Unknown error")
    except json.JSONDecodeError:
        return failed_sql, "Failed to parse error recovery response"
