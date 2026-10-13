from __future__ import annotations

import json
from typing import Any

from llm.base import LLMProvider

SYNTHESIS_SYSTEM_PROMPT = """You are an answer synthesis engine. Convert SQL query results into a clear, natural-language answer.

Given:
- The original question
- The SQL that was executed
- The query results

Produce a human-readable answer that directly addresses the question.

Return JSON: {"answer": "natural language answer", "confidence": 0.0-1.0, "caveats": ["any limitations or notes"]}
"""


def synthesize_answer(
    question: str,
    sql: str,
    rows: list[dict[str, Any]],
    llm: LLMProvider,
) -> dict[str, Any]:
    prompt = f"""Synthesize an answer:

Question: {question}
SQL: {sql}
Results ({len(rows)} rows): {json.dumps(rows[:50], default=str)}

Return only valid JSON."""

    response = llm.generate(prompt=prompt, system_prompt=SYNTHESIS_SYSTEM_PROMPT)

    try:
        data = json.loads(response.content)
    except json.JSONDecodeError:
        data = {
            "answer": f"Query returned {len(rows)} results.",
            "confidence": 0.5,
            "caveats": ["Could not parse synthesis response"],
        }

    return {
        "answer": data.get("answer", "No answer generated"),
        "confidence": data.get("confidence", 0.5),
        "caveats": data.get("caveats", []),
        "sql_executed": sql,
        "row_count": len(rows),
    }
