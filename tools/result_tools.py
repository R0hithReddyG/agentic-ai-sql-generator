from __future__ import annotations

import time
from typing import Any, Optional

from tools.base_tool import ToolOutput
from tools.registry import ToolRegistry


def verify_result_shape(
    rows: list[dict[str, Any]],
    expected_min_columns: int = 1,
    expected_min_rows: int = 0,
) -> ToolOutput:
    start = time.time()
    issues: list[str] = []

    if not isinstance(rows, list):
        issues.append("Result is not a list")
    else:
        if len(rows) < expected_min_rows:
            issues.append(f"Expected at least {expected_min_rows} rows, got {len(rows)}")
        if rows:
            col_count = len(rows[0])
            if col_count < expected_min_columns:
                issues.append(f"Expected at least {expected_min_columns} columns, got {col_count}")

    return ToolOutput(
        tool_name="verify_result_shape",
        success=len(issues) == 0,
        data={"row_count": len(rows) if isinstance(rows, list) else 0, "issues": issues},
        error="; ".join(issues) if issues else None,
        duration_ms=(time.time() - start) * 1000,
    )


def check_aggregation_consistency(
    rows: list[dict[str, Any]],
    aggregation_column: Optional[str] = None,
) -> ToolOutput:
    start = time.time()
    issues: list[str] = []

    if not rows:
        return ToolOutput(
            tool_name="check_aggregation_consistency",
            success=True,
            data={"issues": []},
            duration_ms=(time.time() - start) * 1000,
        )

    if aggregation_column:
        values = [r.get(aggregation_column) for r in rows if r.get(aggregation_column) is not None]
        numeric_values = [v for v in values if isinstance(v, (int, float))]
        if values and not numeric_values:
            issues.append(f"Column '{aggregation_column}' has no numeric values for aggregation check")
        if any(v < 0 for v in numeric_values if isinstance(v, (int, float))):
            pass

    return ToolOutput(
        tool_name="check_aggregation_consistency",
        success=len(issues) == 0,
        data={"issues": issues},
        error="; ".join(issues) if issues else None,
        duration_ms=(time.time() - start) * 1000,
    )


def format_results(
    rows: list[dict[str, Any]],
    max_display: int = 20,
) -> ToolOutput:
    start = time.time()
    display_rows = rows[:max_display]
    truncated = len(rows) > max_display

    return ToolOutput(
        tool_name="format_results",
        success=True,
        data={
            "display_rows": display_rows,
            "total_rows": len(rows),
            "truncated": truncated,
        },
        duration_ms=(time.time() - start) * 1000,
    )


registry = ToolRegistry()
registry.register("verify_result_shape", verify_result_shape)
registry.register("check_aggregation_consistency", check_aggregation_consistency)
registry.register("format_results", format_results)
