import pytest
from database.safety import validate_sql_safety


def test_safe_select():
    is_safe, reason = validate_sql_safety("SELECT * FROM users")
    assert is_safe is True
    assert reason is None


def test_drop_blocked():
    is_safe, reason = validate_sql_safety("DROP TABLE users")
    assert is_safe is False
    assert "Dangerous" in reason


def test_truncate_blocked():
    is_safe, reason = validate_sql_safety("TRUNCATE TABLE orders")
    assert is_safe is False


def test_insert_blocked_by_default():
    is_safe, reason = validate_sql_safety("INSERT INTO users VALUES (1, 'test')")
    assert is_safe is False
    assert "DML" in reason


def test_delete_blocked_by_default():
    is_safe, reason = validate_sql_safety("DELETE FROM users WHERE id = 1")
    assert is_safe is False


def test_with_cte_allowed():
    is_safe, reason = validate_sql_safety("WITH cte AS (SELECT 1) SELECT * FROM cte")
    assert is_safe is True


def test_multiple_statements_blocked():
    is_safe, reason = validate_sql_safety("SELECT 1; SELECT 2")
    assert is_safe is False
