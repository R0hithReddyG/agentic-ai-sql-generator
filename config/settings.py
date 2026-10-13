from __future__ import annotations

import os
from typing import Optional

from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite:///agentic_sql_demo.db"
    )
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_base_url: Optional[str] = os.getenv("OPENAI_BASE_URL")
    max_agent_retries: int = int(os.getenv("MAX_AGENT_RETRIES", "3"))
    max_rows_returned: int = int(os.getenv("MAX_ROWS_RETURNED", "1000"))
    query_timeout_seconds: int = int(os.getenv("QUERY_TIMEOUT_SECONDS", "30"))
    allow_ddl: bool = False
    allow_dml: bool = False
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    dialect: str = os.getenv("SQL_DIALECT", "sqlite")


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
