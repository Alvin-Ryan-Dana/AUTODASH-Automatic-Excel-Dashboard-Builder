"""Dataset profiling and quality checks."""
from __future__ import annotations
import pandas as pd
import numpy as np

def _date_candidate(s: pd.Series) -> bool:
    if pd.api.types.is_datetime64_any_dtype(s):
        return True
    if not (s.dtype == "object" or pd.api.types.is_string_dtype(s)):
        return False
    sample = s.dropna().astype(str).head(200)
    if len(sample) < 3:
        return False
    parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
    return parsed.notna().mean() >= 0.85

def profile_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return per-column profiling table and dataset-level quality summary."""
    rows = []
    for col in df.columns:
        s = df[col]
        nonnull = s.dropna()
        numeric = pd.to_numeric(nonnull, errors="coerce")
        numeric_ratio = numeric.notna().mean() if len(nonnull) else 0
        date_like = _date_candidate(s)
        if pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s):
            kind = "numerik"
        elif date_like:
            kind = "tanggal"
        elif numeric_ratio >= 0.9 and len(nonnull) > 0 and s.nunique(dropna=True) > 20 and s.nunique(dropna=True) > len(s)*0.7:
            kind = "kemungkinan identifier numerik"
        else:
            kind = "teks/kategori"
        nunique = int(s.nunique(dropna=True))
        high_card = nunique > max(20, int(len(df)*0.5))
        identifier = (nunique == len(df) and len(df) >= 20) or (
            "identifier" in kind.lower()) or (nunique >= 20 and nunique / max(len(df), 1) > .95 and "numerik" not in kind)
        outliers = 0
        if kind == "numerik":
            vals = pd.to_numeric(s, errors="coerce").dropna()
            if len(vals) >= 4:
                q1, q3 = vals.quantile([.25, .75])
                iqr = q3-q1
                if iqr > 0:
                    outliers = int(((vals < q1-1.5*iqr) | (vals > q3+1.5*iqr)).sum())
        rows.append({"kolom": str(col), "tipe_terdeteksi": kind, "nilai_kosong": int(s.isna().sum()),
                     "persen_kosong": round(float(s.isna().mean()*100), 2) if len(s) else 0,
                     "nilai_unik": nunique, "kardinalitas_tinggi": bool(high_card),
                     "kandidat_identifier": bool(identifier), "outlier_IQR": outliers})
    profile = pd.DataFrame(rows)
    summary = {"baris": int(len(df)), "kolom": int(len(df.columns)),
               "baris_duplikat": int(df.duplicated().sum()),
               "sel_kosong": int(df.isna().sum().sum()),
               "persen_sel_kosong": round(float(df.isna().sum().sum()/max(df.size, 1)*100), 2)}
    return profile, summary

def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create a compact descriptive-statistics table for numeric columns."""
    cols = df.select_dtypes(include="number").columns
    if len(cols) == 0:
        return pd.DataFrame(columns=["statistik"])
    return df[cols].describe().T.reset_index(names="kolom")
