from __future__ import annotations

import re
from typing import Optional

from config.settings import get_settings

DANGEROUS_PATTERNS = [
    r"\bDROP\b",
    r"\bTRUNCATE\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bxp_",
    r"\bsp_",
    r";\s*--",
    r"/\*.*\*/",
]

DML_PATTERNS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bMERGE\b",
]


class SafetyViolation(Exception):
    pass


def validate_sql_safety(sql: str) -> tuple[bool, Optional[str]]:
    settings = get_settings()
    upper_sql = sql.upper().strip()

    if not upper_sql.startswith("SELECT") and not upper_sql.startswith("WITH"):
        if not settings.allow_dml:
            for pattern in DML_PATTERNS:
                if re.search(pattern, upper_sql, re.IGNORECASE):
                    return False, f"DML statements are not allowed: {pattern}"

    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, upper_sql, re.IGNORECASE):
            return False, f"Dangerous SQL pattern detected: {pattern}"

    if ";" in sql.strip().rstrip(";"):
        remaining = sql.strip().replace(";", " ", 1)
        if remaining.strip():
            return False, "Multiple statements are not allowed"

    return True, None


def sanitize_for_logging(sql: str) -> str:
    return sql[:500] + "..." if len(sql) > 500 else sql
