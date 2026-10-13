from __future__ import annotations

import json
import re
from typing import Any, Optional

from llm.base import LLMProvider, LLMResponse


class MockLLMProvider(LLMProvider):
    def name(self) -> str:
        return "mock"

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> LLMResponse:
        combined = (system_prompt or "") + "\n" + prompt
        lower = combined.lower()

        if "list all tables" in lower or "show tables" in lower or "available tables" in lower:
            content = json.dumps({
                "tables": [
                    "departments", "employees", "customers",
                    "products", "orders", "order_items",
                ]
            })
            return LLMResponse(content=content, model="mock", tokens_used=0)

        if "describe" in lower or "schema" in lower or "columns" in lower:
            content = json.dumps({
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "name", "type": "VARCHAR", "primary_key": False},
                ]
            })
            return LLMResponse(content=content, model="mock", tokens_used=0)

        if "intent" in lower or "analyze" in lower or "understand" in lower:
            content = json.dumps({
                "entities": [],
                "metrics": [],
                "filters": [],
                "aggregations": [],
                "time_constraints": [],
                "join_hints": [],
                "is_ambiguous": False,
                "ambiguity_reasons": [],
                "clarification_questions": [],
            })
            return LLMResponse(content=content, model="mock", tokens_used=0)

        if "plan" in lower or "strategy" in lower or "decompos" in lower:
            content = json.dumps({
                "strategy": "single_query",
                "sub_plans": [
                    {
                        "description": "Execute query",
                        "tables_involved": [],
                        "depends_on": [],
                    }
                ],
                "reasoning": "Direct query approach",
                "estimated_complexity": "low",
            })
            return LLMResponse(content=content, model="mock", tokens_used=0)

        sql_match = re.search(r"SELECT\b.+?;", combined, re.IGNORECASE | re.DOTALL)
        if sql_match:
            content = json.dumps({"sql": sql_match.group(0)})
            return LLMResponse(content=content, model="mock", tokens_used=0)

        if "generate" in lower or "sql" in lower or "write" in lower:
            content = json.dumps({"sql": "SELECT 1"})
            return LLMResponse(content=content, model="mock", tokens_used=0)

        if "valid" in lower or "check" in lower or "verify" in lower:
            content = json.dumps({
                "is_valid": True,
                "issues": [],
                "corrected_sql": None,
            })
            return LLMResponse(content=content, model="mock", tokens_used=0)

        if "error" in lower or "fix" in lower or "correct" in lower or "recover" in lower:
            content = json.dumps({
                "root_cause": "Mock error analysis",
                "corrected_sql": "SELECT 1",
                "explanation": "Mock correction",
            })
            return LLMResponse(content=content, model="mock", tokens_used=0)

        if "synthes" in lower or "answer" in lower or "explain" in lower or "response" in lower:
            content = json.dumps({
                "answer": "Based on the query results, here is the answer.",
                "confidence": 0.9,
                "caveats": [],
            })
            return LLMResponse(content=content, model="mock", tokens_used=0)

        content = json.dumps({"result": "ok"})
        return LLMResponse(content=content, model="mock", tokens_used=0)
