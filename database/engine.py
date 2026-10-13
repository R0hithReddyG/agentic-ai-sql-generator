from __future__ import annotations

from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config.settings import get_settings

_engine: Optional[Engine] = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.database_url,
            echo=False,
            pool_pre_ping=True,
        )
    return _engine


def execute_read_only(sql: str, params: Optional[dict] = None) -> list[dict]:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        columns = list(result.keys())
        rows = []
        max_rows = get_settings().max_rows_returned
        for i, row in enumerate(result):
            if i >= max_rows:
                break
            rows.append(dict(zip(columns, row)))
        return rows


def get_raw_connection():
    return get_engine().connect()
