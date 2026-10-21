"""Safe JSON dashboard configuration persistence."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

def save_config(config: dict, path: str | Path) -> None:
    """Write JSON configuration; dataset values are not included."""
    Path(path).write_text(json.dumps(config, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

def load_config(path_or_text: str | Path, columns: list[str], from_text: bool = False) -> dict:
    """Load and validate a configuration from a file path or JSON text."""
    raw = json.loads(str(path_or_text)) if from_text else json.loads(Path(path_or_text).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("charts", []), list):
        raise ValueError("Struktur konfigurasi tidak valid.")
    for chart in raw.get("charts", []):
        if not isinstance(chart, dict):
            raise ValueError("Konfigurasi grafik tidak valid.")
        for key in ("x", "y", "color"):
            if chart.get(key) and chart[key] not in columns:
                raise ValueError(f"Konfigurasi merujuk kolom yang tidak tersedia: {chart[key]}")
    return raw
