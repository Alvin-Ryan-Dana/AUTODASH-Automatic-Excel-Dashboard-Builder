"""Validation helpers for dashboard configuration."""
from __future__ import annotations
VALID_CHARTS = {"bar", "line", "scatter", "histogram", "box", "pie", "heatmap", "table"}

def validate_chart_config(config: dict, columns: list[str]) -> tuple[bool, str]:
    chart = config.get("chart_type")
    if chart not in VALID_CHARTS:
        return False, "Jenis grafik tidak dikenal."
    for key in ("x", "y", "color"):
        value = config.get(key)
        if value and value not in columns:
            return False, f"Kolom {key.upper()} '{value}' tidak ditemukan dalam dataset."
    if chart in {"bar", "line", "scatter"} and not config.get("x"):
        return False, "Grafik ini memerlukan kolom X."
    if chart in {"bar", "line", "scatter"} and not config.get("y"):
        return False, "Grafik ini memerlukan kolom Y."
    if chart in {"histogram", "box"} and not (config.get("x") or config.get("y")):
        return False, f"{chart} memerlukan kolom numerik."
    return True, ""
