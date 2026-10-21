"""Transparent descriptive insights; no causal claims."""
from __future__ import annotations
import pandas as pd

def generate_insights(df: pd.DataFrame, profile: pd.DataFrame) -> list[str]:
    """Create short statistical observations supported by the current data."""
    if df.empty:
        return ["Tidak ada baris untuk dianalisis setelah filter diterapkan."]
    out = [f"Dataset yang sedang ditampilkan berisi {len(df):,} baris dan {len(df.columns)} kolom."]
    if "nilai_kosong" in profile and len(profile):
        row = profile.sort_values("nilai_kosong", ascending=False).iloc[0]
        if row["nilai_kosong"] > 0:
            out.append(f"Kolom dengan nilai kosong terbanyak: '{row['kolom']}' ({int(row['nilai_kosong']):,} nilai).")
    for col in df.select_dtypes(include="number").columns[:5]:
        s = df[col].dropna()
        if len(s):
            out.append(f"'{col}': minimum {s.min():,.3g}, maksimum {s.max():,.3g}, median {s.median():,.3g}.")
    for col in df.select_dtypes(exclude="number").columns[:3]:
        vc = df[col].fillna("(Kosong)").astype(str).value_counts()
        if len(vc):
            out.append(f"Nilai paling sering pada '{col}': {vc.index[0]} ({vc.iloc[0]:,} baris).")
    nums = df.select_dtypes(include="number")
    if nums.shape[1] >= 2:
        corr = nums.corr(numeric_only=True)
        pairs = [(corr.iloc[i,j], corr.index[i], corr.columns[j]) for i in range(len(corr)) for j in range(i+1,len(corr)) if pd.notna(corr.iloc[i,j])]
        if pairs:
            value, a, b = max(pairs, key=lambda x: abs(x[0]))
            if abs(value) >= .7:
                out.append(f"Korelasi linear relatif kuat teramati antara '{a}' dan '{b}' (r={value:.2f}); ini bukan bukti sebab-akibat.")
    return out
