"""Rule-based automatic chart recommendations."""
from __future__ import annotations
import pandas as pd
from .data_profiler import profile_dataset

def recommend_charts(df: pd.DataFrame, limit: int = 6) -> list[dict]:
    """Recommend a small set of useful charts without relying on column names."""
    if df.empty or len(df.columns) == 0:
        return []
    profile, _ = profile_dataset(df)
    kinds = dict(zip(profile["kolom"], profile["tipe_terdeteksi"]))
    numeric = [c for c in df.select_dtypes(include="number").columns if not profile.set_index("kolom").loc[c, "kandidat_identifier"]]
    dates = [c for c in df.columns if kinds.get(c) == "tanggal"]
    categories = [c for c in df.columns if kinds.get(c) == "teks/kategori" and df[c].nunique(dropna=True) <= min(30, max(2, len(df)//2))]
    recs = []
    if numeric:
        metric = max(numeric, key=lambda c: df[c].notna().sum())
        recs.append({"title": f"Distribusi {metric}", "chart_type": "histogram", "x": metric, "y": None, "aggregation": "count"})
    if dates and numeric:
        recs.append({"title": f"{numeric[0]} sepanjang waktu", "chart_type": "line", "x": dates[0], "y": numeric[0], "aggregation": "mean"})
    if categories and numeric:
        recs.append({"title": f"{numeric[0]} menurut {categories[0]}", "chart_type": "bar", "x": categories[0], "y": numeric[0], "aggregation": "sum"})
    elif categories:
        recs.append({"title": f"Frekuensi {categories[0]}", "chart_type": "bar", "x": categories[0], "y": None, "aggregation": "count"})
    if len(numeric) >= 2:
        recs.append({"title": f"Hubungan {numeric[0]} dan {numeric[1]}", "chart_type": "scatter", "x": numeric[0], "y": numeric[1], "aggregation": "mean"})
    if len(numeric) >= 3:
        recs.append({"title": "Korelasi antar kolom numerik", "chart_type": "heatmap", "x": None, "y": None, "aggregation": "mean"})
    recs.append({"title": "Pratinjau data", "chart_type": "table", "x": None, "y": None, "aggregation": "count"})
    return recs[:limit]
