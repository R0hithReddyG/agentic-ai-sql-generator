from __future__ import annotations

import json
from typing import Any, Optional

from llm.base import LLMProvider
from state.agent_state import ExecutionPlan, SubPlan

PLANNER_SYSTEM_PROMPT = """You are a SQL query planner. Given a natural language question and database schema, create an execution plan.

Return JSON with this exact structure:
{
  "strategy": "single_query" or "multi_step",
  "sub_plans": [
    {
      "description": "what this step does",
      "tables_involved": ["table1", "table2"],
      "depends_on": []
    }
  ],
  "reasoning": "why this plan was chosen",
  "estimated_complexity": "low" or "medium" or "high"
}
"""


def create_execution_plan(
    question: str,
    schema_context: dict[str, Any],
    intent: dict[str, Any],
    llm: LLMProvider,
) -> ExecutionPlan:
    prompt = f"""Question: {question}

Schema Context:
{json.dumps(schema_context, indent=2, default=str)}

Intent Analysis:
{json.dumps(intent, indent=2, default=str)}

Create an execution plan. Return only valid JSON."""

    response = llm.generate(prompt=prompt, system_prompt=PLANNER_SYSTEM_PROMPT)

    try:
        plan_data = json.loads(response.content)
    except json.JSONDecodeError:
        plan_data = {
            "strategy": "single_query",
            "sub_plans": [{"description": "Execute query", "tables_involved": [], "depends_on": []}],
            "reasoning": "Fallback plan due to parse error",
            "estimated_complexity": "low",
        }

    sub_plans = []
    for sp in plan_data.get("sub_plans", []):
        sub_plans.append(SubPlan(
            description=sp.get("description", ""),
            tables_involved=sp.get("tables_involved", []),
            depends_on=sp.get("depends_on", []),
        ))

    return ExecutionPlan(
        strategy=plan_data.get("strategy", "single_query"),
        sub_plans=sub_plans,
        reasoning=plan_data.get("reasoning", ""),
        estimated_complexity=plan_data.get("estimated_complexity", "low"),
    )
