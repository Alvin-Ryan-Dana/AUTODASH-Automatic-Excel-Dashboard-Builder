"""CSV and self-contained HTML report export."""
from __future__ import annotations
import json
import pandas as pd

def dataframe_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")

def html_report(title: str, df: pd.DataFrame, insights: list[str], config: dict) -> bytes:
    """Generate a standalone HTML report with escaped text and embedded table."""
    safe_title = (title or "AutoDash").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    table = df.head(500).to_html(index=False, escape=True, border=0, classes="data")
    items = "".join(f"<li>{str(x).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')}</li>" for x in insights)
    cfg = json.dumps(config, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    html = f"""<!doctype html><html lang="id"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>{safe_title}</title><style>body{{font:16px system-ui;max-width:1200px;margin:2rem auto;padding:0 1rem;color:#172033}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:.5rem;border-bottom:1px solid #ddd;text-align:left}}th{{background:#eef2f7}}pre{{white-space:pre-wrap;background:#f6f8fb;padding:1rem}}</style>
<h1>{safe_title}</h1><p>Baris dalam laporan: {len(df)}. Tabel dibatasi 500 baris.</p><h2>Insight</h2><ul>{items}</ul><h2>Data</h2>{table}<h2>Konfigurasi dashboard</h2><pre>{cfg}</pre></html>"""
    return html.encode("utf-8")
