# Agentic SQL Query Generator

Production-oriented agentic AI system that converts natural language questions into SQL queries through autonomous planning, tool use, iterative error recovery, and result verification.

## Architecture

```
User Question
     │
     ▼
┌─────────────────┐
│  Orchestrator    │ ◄── Main ReAct Loop
│  Agent           │
└────┬────────────┘
     │
     ├──► Intent Analysis (LLM)
     ├──► Schema Discovery (DB Tools)
     ├──► Query Planning (LLM + Decomposer)
     ├──► SQL Generation (LLM, schema-grounded)
     ├──► SQL Validation (sqlglot + LLM + Safety)
     ├──► Query Execution (Read-only DB)
     │       │
     │       ├── SUCCESS ──► Result Verification ──► Answer Synthesis
     │       │
     │       └── ERROR ──► Error Recovery (LLM) ──► Retry (bounded)
     │
     └──► Final Answer + Full Execution Trace
```

### Agent State Machine

The agent progresses through explicit states: `IDLE → INTENT_ANALYSIS → SCHEMA_DISCOVERY → PLANNING → SQL_GENERATION → VALIDATION → EXECUTION → RESULT_VERIFICATION → ANSWER_SYNTHESIS → COMPLETED`. On failure, it transitions to `ERROR_RECOVERY` and loops back with bounded retries.

### Why This Design vs Alternatives

| Approach | Pros | Cons |
|----------|------|------|
| **Single LLM call** | Fast, simple | Hallucinates schemas, no error recovery, no verification |
| **LangChain chain** | Modular | Hidden state, hard to debug, vendor lock-in |
| **This ReAct agent** | Observable, safe, self-correcting | More latency, requires LLM |

## Project Structure

```
agentic-sql/
├── agents/              # Agent modules (orchestrator, planner, generator, etc.)
│   ├── orchestrator.py  # Core ReAct loop
│   ├── schema_agent.py  # Intent analysis
│   ├── planner_agent.py # Schema discovery
│   ├── generator_agent.py # SQL generation
│   ├── validator_agent.py # SQL validation
│   ├── executor_agent.py  # Query execution wrapper
│   ├── verifier_agent.py  # Result verification
│   ├── error_recovery.py  # Autonomous error fixing
│   └── synthesizer.py     # Answer synthesis
├── config/              # Configuration
│   ├── settings.py      # Pydantic settings
│   └── default_schema.sql
├── database/            # Database layer
│   ├── engine.py        # SQLAlchemy engine
│   ├── models.py        # ORM models (6 tables)
│   ├── safety.py        # SQL safety validation
│   └── seed.py          # Sample data seeder
├── eval/                # Evaluation & benchmarks
│   └── benchmark.py
├── examples/            # Example traces
│   └── traces.json
├── llm/                 # LLM abstraction
│   ├── base.py          # Abstract provider
│   ├── factory.py       # Provider factory
│   ├── mock_provider.py # Deterministic mock
│   └── openai_provider.py # OpenAI integration
├── plan/                # Query planning
│   └── decomposer.py
├── services/            # API layer
│   ├── api.py           # FastAPI app
│   └── query_service.py # Business logic
├── state/               # Agent state
│   ├── agent_state.py   # Typed state models
│   └── memory.py        # Persistent memory
├── tests/               # Test suite
├── tools/               # Tool definitions
│   ├── base_tool.py     # Base classes
│   ├── registry.py      # Tool registry
│   ├── schema_tools.py  # Schema inspection
│   ├── execution_tools.py # SQL execution/validation
│   ├── result_tools.py  # Result verification
│   └── trace_tool.py    # Tracing
├── ui/                  # Frontend
│   └── streamlit_app.py
├── main.py              # CLI entry points
└── pyproject.toml
```

## Setup

```bash
pip install -e ".[dev,openai]"
```

## Usage

### CLI

```bash
python main.py -q "How many employees are in each department?"
```

### Demo

```bash
python main.py --demo
# or: run-demo
```

### API Server

```bash
python -c "from main import run_server; run_server()"
# or: run-server
```

Then POST to `http://localhost:8000/query`:
```json
{"question": "Top 5 customers by revenue"}
```

### Streamlit UI

```bash
streamlit run ui/streamlit_app.py
```

### Benchmark

```bash
python -c "from main import run_benchmark; run_benchmark()"
# or: run-benchmark
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///agentic_sql_demo.db` | Database connection string |
| `LLM_PROVIDER` | `mock` | `mock` or `openai` |
| `OPENAI_API_KEY` | - | Required for OpenAI provider |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model name |
| `OPENAI_BASE_URL` | - | Custom API base URL |
| `MAX_AGENT_RETRIES` | `3` | Max error recovery attempts |
| `SQL_DIALECT` | `sqlite` | Target SQL dialect |
| `API_HOST` | `0.0.0.0` | Server host |
| `API_PORT` | `8000` | Server port |

## Database Schema

6 interconnected tables seeded with realistic data:
- **departments** (5 rows) - Company departments
- **employees** (50 rows) - Staff with salaries, titles, hire dates
- **customers** (100 rows) - Global customer base
- **products** (30 rows) - Multi-category product catalog
- **orders** (200 rows) - Transactional orders
- **order_items** (~600 rows) - Line items with quantities, prices, discounts

## Security

- Read-only query execution enforced at the database layer
- SQL safety validation blocks DDL, DML, dangerous patterns (DROP, TRUNCATE, EXEC, etc.)
- Multiple statement injection prevention
- Bounded retry limits prevent runaway execution
- No secrets logged or exposed in traces

## Tests

```bash
pytest tests/ -v
```

## Limitations & Future Work

- Currently supports SQLite primarily; PostgreSQL adapter exists but needs testing
- Mock LLM returns deterministic responses; real evaluation requires OpenAI/local models
- No multi-turn conversation memory across sessions
- No streaming responses
- Future: Add LangGraph/LangSmith observability, support more dialects, add caching layer
