from __future__ import annotations

from typing import Any, Optional


class PersistentMemory:
    def __init__(self) -> None:
        self._store: dict[str, Any] = {}
        self._schema_cache: Optional[dict[str, Any]] = None
        self._query_history: list[dict[str, Any]] = []

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def has(self, key: str) -> bool:
        return key in self._store

    def clear(self) -> None:
        self._store.clear()
        self._schema_cache = None
        self._query_history.clear()

    @property
    def schema_cache(self) -> Optional[dict[str, Any]]:
        return self._schema_cache

    @schema_cache.setter
    def schema_cache(self, value: dict[str, Any]) -> None:
        self._schema_cache = value

    def add_query_to_history(
        self, question: str, sql: str, success: bool
    ) -> None:
        self._query_history.append(
            {"question": question, "sql": sql, "success": success}
        )

    @property
    def query_history(self) -> list[dict[str, Any]]:
        return list(self._query_history)
