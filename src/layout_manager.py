"""Dashboard layout utilities."""
from __future__ import annotations

def normalize_layout(items: list[dict]) -> list[dict]:
    """Normalize visibility and ordering; preserve chart settings."""
    return [dict(item, visible=bool(item.get("visible", True)), order=i) for i, item in enumerate(items)]

def move_item(items: list[dict], index: int, direction: int) -> list[dict]:
    """Move an item up (-1) or down (+1), safely."""
    result = [dict(x) for x in items]
    target = index + direction
    if 0 <= index < len(result) and 0 <= target < len(result):
        result[index], result[target] = result[target], result[index]
    return normalize_layout(result)
