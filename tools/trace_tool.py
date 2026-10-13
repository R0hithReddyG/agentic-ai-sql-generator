from __future__ import annotations

import json
import time
from typing import Any

from tools.base_tool import ToolOutput
from tools.registry import ToolRegistry


def record_trace(
    session_id: str,
    phase: str,
    data: dict[str, Any],
) -> ToolOutput:
    start = time.time()
    trace_entry = {
        "session_id": session_id,
        "phase": phase,
        "timestamp": time.time(),
        "data": data,
    }
    return ToolOutput(
        tool_name="record_trace",
        success=True,
        data=trace_entry,
        duration_ms=(time.time() - start) * 1000,
    )


def export_trace(trace_log: list[dict[str, Any]]) -> ToolOutput:
    start = time.time()
    try:
        output = json.dumps(trace_log, indent=2, default=str)
        return ToolOutput(
            tool_name="export_trace",
            success=True,
            data=output,
            duration_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        return ToolOutput(
            tool_name="export_trace",
            success=False,
            error=str(e),
            duration_ms=(time.time() - start) * 1000,
        )


registry = ToolRegistry()
registry.register("record_trace", record_trace)
registry.register("export_trace", export_trace)
