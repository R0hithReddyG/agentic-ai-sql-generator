import pytest
from tools.registry import ToolRegistry


def test_registry_singleton():
    r1 = ToolRegistry()
    r2 = ToolRegistry()
    assert r1 is r2


def test_register_and_get():
    registry = ToolRegistry()

    def dummy_tool(x: int = 0) -> int:
        return x * 2

    registry.register("dummy_test_tool", dummy_tool)
    assert registry.get("dummy_test_tool") is dummy_tool


def test_execute():
    registry = ToolRegistry()

    def add(a: int = 0, b: int = 0) -> int:
        return a + b

    registry.register("add_tool", add)
    result = registry.execute("add_tool", a=3, b=4)
    assert result == 7


def test_unknown_tool_raises():
    registry = ToolRegistry()
    with pytest.raises(ValueError, match="Unknown tool"):
        registry.execute("nonexistent_tool_xyz")
