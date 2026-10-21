"""Validated Plotly chart construction."""
from __future__ import annotations
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .validators import validate_chart_config

AGGREGATIONS = {"sum": "sum", "mean": "mean", "median": "median", "count": "count", "min": "min", "max": "max"}

_INDONESIAN_MONTHS = {
    "januari": "January", "februari": "February", "maret": "March",
    "april": "April", "mei": "May", "juni": "June", "juli": "July",
    "agustus": "August", "september": "September", "oktober": "October",
    "november": "November", "desember": "December",
}


def _as_datetime_if_recognizable(series: pd.Series) -> pd.Series:
    """Parse recognizable date strings without guessing from ordinary categories."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return series
    if not (pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)):
        return series

    values = series.astype("string").str.strip()
    for local_month, english_month in _INDONESIAN_MONTHS.items():
        values = values.str.replace(local_month, english_month, case=False, regex=False)

    # dayfirst=True suits common Indonesian/Excel dates (DD/MM/YYYY); ISO dates
    # remain correctly interpreted. format='mixed' supports multiple formats in
    # the same column (available in the project's pinned Pandas 2.2+).
    parsed = pd.to_datetime(values, errors="coerce", format="mixed", dayfirst=True)
    non_null = series.notna()
    if int(non_null.sum()) >= 2 and parsed[non_null].notna().mean() >= 0.8:
        return parsed
    return series

def build_chart(df: pd.DataFrame, config: dict):
    """Build a Plotly figure, raising ValueError for incompatible settings."""
    ok, message = validate_chart_config(config, list(df.columns))
    if not ok:
        raise ValueError(message)
    kind = config["chart_type"]
    x, y, color = config.get("x"), config.get("y"), config.get("color") or None
    title = config.get("title") or "Visualisasi"
    limit = int(config.get("category_limit", 20))
    work = df.copy()
    if kind == "table":
        return None
    if kind == "heatmap":
        nums = work.select_dtypes(include="number")
        if nums.shape[1] < 2:
            raise ValueError("Heatmap membutuhkan minimal dua kolom numerik.")
        fig = px.imshow(nums.corr(numeric_only=True), text_auto=".2f", aspect="auto", title=title, color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
    elif kind == "histogram":
        col = x or y
        if not pd.api.types.is_numeric_dtype(work[col]):
            raise ValueError("Histogram memerlukan kolom numerik.")
        fig = px.histogram(work, x=col, color=color if color in work.columns else None, title=title)
    elif kind == "box":
        col = x or y
        if not pd.api.types.is_numeric_dtype(work[col]):
            raise ValueError("Box plot memerlukan kolom numerik.")
        fig = px.box(work, y=col, x=(config.get("group") if config.get("group") in work.columns else None), color=color, title=title)
    elif kind == "scatter":
        if not pd.api.types.is_numeric_dtype(work[y]) or not pd.api.types.is_numeric_dtype(work[x]):
            raise ValueError("Scatter plot memerlukan X dan Y numerik.")
        fig = px.scatter(work, x=x, y=y, color=color, title=title)
    elif kind in {"bar", "line", "pie"}:
        if kind == "pie":
            if not x:
                raise ValueError("Pie chart memerlukan kolom kategori pada X.")
            counts = work[x].fillna("(Kosong)").astype(str).value_counts().head(limit)
            fig = px.pie(names=counts.index, values=counts.values, title=title)
        elif y:
            if kind == "line":
                # Work on this chart's copy only; keep the source DataFrame intact.
                work[x] = _as_datetime_if_recognizable(work[x])
            if config.get("aggregation") == "count":
                grouped = work.groupby(x, dropna=False, sort=False)[y].count().reset_index(name="nilai")
            else:
                agg = config.get("aggregation", "sum")
                if agg not in AGGREGATIONS:
                    raise ValueError("Agregasi tidak valid.")
                grouped = work.groupby(x, dropna=False, sort=False)[y].agg(AGGREGATIONS[agg]).reset_index(name="nilai")
            if kind == "bar":
                grouped = grouped.sort_values("nilai", ascending=False).head(limit)
            else:
                # Datetime X gives Plotly a true continuous time axis. Sorting
                # the parsed values ensures chronology; duplicate dates have
                # already been combined using the selected aggregation.
                grouped = grouped.sort_values(x, kind="stable", na_position="last")
            fig = px.bar(grouped, x=x, y="nilai", color=color if color in grouped.columns else None, title=title) if kind == "bar" else px.line(grouped, x=x, y="nilai", markers=True, title=title)
            if kind == "line" and pd.api.types.is_datetime64_any_dtype(grouped[x]):
                fig.update_xaxes(type="date")
        else:
            counts = work[x].fillna("(Kosong)").astype(str).value_counts().head(limit).rename_axis(x).reset_index(name="frekuensi")
            fig = px.bar(counts, x=x, y="frekuensi", title=title)
    else:
        raise ValueError("Jenis grafik tidak didukung.")
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20), legend_title_text=config.get("color_label") or "Kategori")
    if config.get("x_label"): fig.update_xaxes(title=config["x_label"])
    if config.get("y_label"): fig.update_yaxes(title=config["y_label"])
    return fig
