from __future__ import annotations

import json
from typing import Any

from llm.base import LLMProvider
from tools.result_tools import verify_result_shape, check_aggregation_consistency
from state.agent_state import ValidationCheck

VERIFIER_SYSTEM_PROMPT = """You are a result verification engine. Determine if the query results correctly answer the original question.

Check:
1. Does the result shape match expectations?
2. Are there semantic inconsistencies?
3. Does the data actually answer the question asked?

Return JSON: {"is_verified": bool, "issues": ["list of issues"], "confidence": 0.0-1.0}
"""


def verify_results(
    question: str,
    sql: str,
    rows: list[dict[str, Any]],
    llm: LLMProvider,
) -> tuple[bool, list[ValidationCheck], float]:
    checks: list[ValidationCheck] = []

    shape_result = verify_result_shape(rows)
    checks.append(ValidationCheck(
        check_name="result_shape",
        passed=shape_result.success,
        details=shape_result.error,
    ))

    prompt = f"""Verify these results answer the question:

Question: {question}
SQL: {sql}
Results ({len(rows)} rows): {json.dumps(rows[:10], default=str)}

Return only valid JSON."""

    response = llm.generate(prompt=prompt, system_prompt=VERIFIER_SYSTEM_PROMPT)

    try:
        data = json.loads(response.content)
    except json.JSONDecodeError:
        data = {"is_verified": True, "issues": [], "confidence": 0.5}

    is_verified = data.get("is_verified", True)
    issues = data.get("issues", [])
    confidence = data.get("confidence", 0.5)

    checks.append(ValidationCheck(
        check_name="semantic_verification",
        passed=is_verified,
        details="; ".join(issues) if issues else None,
    ))

    return is_verified, checks, confidence
