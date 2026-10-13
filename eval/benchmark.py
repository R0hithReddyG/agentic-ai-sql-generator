from __future__ import annotations

import json
import time
from typing import Any

from agents.orchestrator import OrchestratorAgent
from llm.factory import get_llm_provider, set_llm_provider
from llm.mock_provider import MockLLMProvider
from state.agent_state import AgentStatus

BENCHMARK_QUESTIONS = [
    "How many employees are in each department?",
    "What is the total revenue from all orders?",
    "List the top 5 customers by order count.",
    "What is the average salary per department?",
    "Show all orders placed in 2024.",
    "Which products have never been ordered?",
    "What is the total discount given across all orders?",
    "Find employees hired after 2022-01-01 with salary above 80000.",
    "How many orders does each customer have?",
    "What are the categories of products and their average price?",
]


def run_benchmark() -> dict[str, Any]:
    set_llm_provider(MockLLMProvider())
    orchestrator = OrchestratorAgent(max_retries=3)

    results = []
    total_start = time.time()

    for question in BENCHMARK_QUESTIONS:
        start = time.time()
        state = orchestrator.process(question)
        duration = time.time() - start

        results.append({
            "question": question,
            "status": state.status.value,
            "success": state.status == AgentStatus.COMPLETED,
            "sql": state.current_sql,
            "row_count": state.row_count,
            "tool_calls": len(state.tool_call_log),
            "errors": len(state.errors),
            "corrections": len(state.correction_attempts),
            "duration_seconds": round(duration, 3),
        })

    total_duration = time.time() - total_start
    successes = sum(1 for r in results if r["success"])

    return {
        "total_questions": len(BENCHMARK_QUESTIONS),
        "successes": successes,
        "failures": len(BENCHMARK_QUESTIONS) - successes,
        "success_rate": round(successes / len(BENCHMARK_QUESTIONS), 4),
        "total_duration_seconds": round(total_duration, 3),
        "avg_duration_seconds": round(total_duration / len(BENCHMARK_QUESTIONS), 3),
        "results": results,
    }


def compare_architectures() -> dict[str, Any]:
    mock = MockLLMProvider()

    architectures = {
        "react_agent": "Full ReAct loop with tool use and error recovery",
        "direct_generation": "Single LLM call without tools",
        "pipeline": "Sequential pipeline without retry logic",
    }

    comparison: dict[str, Any] = {}
    for arch_name, description in architectures.items():
        set_llm_provider(mock)
        orchestrator = OrchestratorAgent(max_retries=3 if arch_name == "react_agent" else 0)

        start = time.time()
        successes = 0
        for q in BENCHMARK_QUESTIONS[:5]:
            state = orchestrator.process(q)
            if state.status == AgentStatus.COMPLETED:
                successes += 1
        duration = time.time() - start

        comparison[arch_name] = {
            "description": description,
            "success_rate": successes / 5,
            "duration_seconds": round(duration, 3),
        }

    return comparison
