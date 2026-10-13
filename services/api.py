from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Optional

from services.query_service import QueryRequest, QueryResponse, process_query
from database.seed import seed_database

app = FastAPI(
    title="Agentic SQL Query Generator",
    description="AI-powered text-to-SQL agent with autonomous error recovery",
    version="0.1.0",
)


@app.on_event("startup")
def startup() -> None:
    seed_database()


@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest) -> QueryResponse:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    return process_query(request)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/schema")
def get_schema() -> dict[str, Any]:
    from tools.schema_tools import get_full_schema
    result = get_full_schema()
    if result.success:
        return result.data or {}
    raise HTTPException(status_code=500, detail=result.error)
