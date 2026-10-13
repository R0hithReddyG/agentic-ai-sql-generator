from __future__ import annotations

import argparse
import json
import logging
import sys

from database.seed import seed_database
from llm.factory import set_llm_provider
from llm.mock_provider import MockLLMProvider


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic SQL Query Generator")
    parser.add_argument("--question", "-q", type=str, help="Natural language question")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    setup_logging(args.log_level)
    set_llm_provider(MockLLMProvider())
    seed_database()

    if args.question:
        from agents.orchestrator import OrchestratorAgent
        orchestrator = OrchestratorAgent()
        state = orchestrator.process(args.question)

        print(f"\nStatus: {state.status.value}")
        print(f"Answer: {state.final_answer}")
        if state.current_sql:
            print(f"SQL: {state.current_sql}")
        print(f"Rows: {state.row_count}")
        print(f"Tool calls: {len(state.tool_call_log)}")
        print(f"Errors: {len(state.errors)}")
        print(f"Corrections: {len(state.correction_attempts)}")

        if state.query_results:
            print(f"\nResults (first 5):")
            for row in state.query_results[:5]:
                print(f"  {row}")
    else:
        parser.print_help()


def run_demo() -> None:
    setup_logging("INFO")
    set_llm_provider(MockLLMProvider())
    seed_database()

    from agents.orchestrator import OrchestratorAgent

    questions = [
        "How many employees are in each department?",
        "What is the total revenue from all orders?",
        "List the top 5 customers by order count.",
    ]

    orchestrator = OrchestratorAgent()
    for q in questions:
        print(f"\n{'='*60}")
        print(f"Question: {q}")
        print('='*60)
        state = orchestrator.process(q)
        print(f"Status: {state.status.value}")
        print(f"Answer: {state.final_answer}")
        if state.current_sql:
            print(f"SQL: {state.current_sql}")
        print(f"Tool calls made: {len(state.tool_call_log)}")


def run_benchmark() -> None:
    setup_logging("WARNING")
    set_llm_provider(MockLLMProvider())
    seed_database()

    from eval.benchmark import run_benchmark as bench, compare_architectures

    print("Running benchmark...")
    results = bench()
    print(json.dumps(results, indent=2))

    print("\nArchitecture comparison:")
    comparison = compare_architectures()
    print(json.dumps(comparison, indent=2))


def run_server() -> None:
    import uvicorn
    from config.settings import get_settings

    setup_logging("INFO")
    set_llm_provider(MockLLMProvider())
    seed_database()

    settings = get_settings()
    uvicorn.run(
        "services.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
