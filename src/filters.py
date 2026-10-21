"""Non-destructive, composable dataset filters."""
from __future__ import annotations
import pandas as pd

def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply categorical, numeric-range, date-range, and text filters."""
    result = df
    for col, spec in (filters or {}).items():
        if col not in result.columns or not isinstance(spec, dict):
            continue
        kind = spec.get("type")
        if kind == "category":
            values = spec.get("values", [])
            if values:
                result = result[result[col].isin(values) | (result[col].isna() & ("(Kosong)" in values))]
        elif kind == "numeric":
            series = pd.to_numeric(result[col], errors="coerce")
            low, high = spec.get("min"), spec.get("max")
            mask = series.notna()
            if low is not None: mask &= series >= low
            if high is not None: mask &= series <= high
            if spec.get("include_missing"): mask |= series.isna()
            result = result[mask]
        elif kind == "date":
            series = pd.to_datetime(result[col], errors="coerce")
            mask = series.notna()
            if spec.get("start"): mask &= series >= pd.Timestamp(spec["start"])
            if spec.get("end"): mask &= series <= pd.Timestamp(spec["end"]) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
            if spec.get("include_missing"): mask |= series.isna()
            result = result[mask]
        elif kind == "text" and spec.get("query"):
            result = result[result[col].astype("string").str.contains(str(spec["query"]), case=False, na=False, regex=False)]
    return result.copy()
