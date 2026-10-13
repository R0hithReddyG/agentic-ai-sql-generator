from __future__ import annotations

import json
from typing import Any

from llm.base import LLMProvider
from state.agent_state import AgentState, IntentAnalysis

INTENT_SYSTEM_PROMPT = """You are an intent analysis engine for a text-to-SQL system.
Analyze the user's natural language question and extract structured intent.

Return ONLY valid JSON with this exact structure:
{
  "entities": ["business entities mentioned"],
  "metrics": ["measurements or KPIs requested"],
  "filters": ["conditions or constraints"],
  "aggregations": ["SUM, COUNT, AVG, etc."],
  "time_constraints": ["date ranges or time references"],
  "join_hints": ["implied relationships between tables"],
  "is_ambiguous": false,
  "ambiguity_reasons": [],
  "clarification_questions": []
}

If the question is ambiguous, set is_ambiguous to true and populate clarification_questions.
"""


def analyze_intent(question: str, llm: LLMProvider) -> IntentAnalysis:
    response = llm.generate(
        prompt=f"Analyze this question: {question}\n\nReturn only valid JSON.",
        system_prompt=INTENT_SYSTEM_PROMPT,
    )

    try:
        data = json.loads(response.content)
    except json.JSONDecodeError:
        data = {
            "entities": [],
            "metrics": [],
            "filters": [],
            "aggregations": [],
            "time_constraints": [],
            "join_hints": [],
            "is_ambiguous": False,
            "ambiguity_reasons": ["Failed to parse LLM response"],
            "clarification_questions": [],
        }

    return IntentAnalysis(
        original_question=question,
        entities=data.get("entities", []),
        metrics=data.get("metrics", []),
        filters=data.get("filters", []),
        aggregations=data.get("aggregations", []),
        time_constraints=data.get("time_constraints", []),
        join_hints=data.get("join_hints", []),
        is_ambiguous=data.get("is_ambiguous", False),
        ambiguity_reasons=data.get("ambiguity_reasons", []),
        clarification_questions=data.get("clarification_questions", []),
    )
