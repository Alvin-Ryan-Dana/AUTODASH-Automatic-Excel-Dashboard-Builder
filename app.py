from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from src.data_loader import read_dataset
from src.data_profiler import profile_dataset, numeric_summary
from src.chart_recommender import recommend_charts
from src.chart_builder import build_chart
from src.dashboard_generator import generate_dashboard
from src.filters import apply_filters
from src.layout_manager import move_item, normalize_layout
from src.dashboard_storage import load_config
from src.insights import generate_insights
from src.exporters import dataframe_csv, html_report
from src.validators import VALID_CHARTS

st.set_page_config(page_title="AutoDash", page_icon="📊", layout="wide")
st.markdown("""<style>
.block-container{padding-top:1.4rem;padding-bottom:3rem}
[data-testid="stMetric"]{background:linear-gradient(135deg,#f8fafc,#eef4ff);padding:1rem;border-radius:14px;border:1px solid #e3eaf5}
section[data-testid="stSidebar"]{border-right:1px solid #e8edf4}
h1,h2,h3{letter-spacing:-.025em}
</style>""", unsafe_allow_html=True)
st.title("📊 AutoDash")
st.caption("Automatic Excel Dashboard Builder · Analisis lokal, tanpa mengirim data ke layanan eksternal")

MAX_MB = int(st.sidebar.number_input("Batas ukuran file (MB)", min_value=1, max_value=500, value=50))
uploaded = st.sidebar.file_uploader("Unggah dataset", type=["csv", "xlsx", "xls"], help="CSV, Excel XLSX, atau XLS")
if "df" not in st.session_state: st.session_state.df = None
if "file_key" not in st.session_state: st.session_state.file_key = None
if "filters" not in st.session_state: st.session_state.filters = {}
if "dashboard" not in st.session_state: st.session_state.dashboard = None

if uploaded is not None:
    if uploaded.size > MAX_MB * 1024 * 1024:
        st.error(f"File melebihi batas {MAX_MB} MB. Ubah batas atau pilih file yang lebih kecil.")
        st.stop()
    key = f"{uploaded.name}:{uploaded.size}"
    if st.session_state.file_key != key:
        try:
            raw = uploaded.getvalue()
            if uploaded.name.lower().endswith((".xlsx", ".xls")):
                try:
                    xl = pd.ExcelFile(raw, engine="openpyxl" if uploaded.name.lower().endswith(".xlsx") else "xlrd")
                    sheet = st.sidebar.selectbox("Sheet Excel", xl.sheet_names, key="sheet_choice")
                    df = read_dataset(raw, uploaded.name, sheet)
                except ImportError:
                    df = read_dataset(raw, uploaded.name)
            else:
                df = read_dataset(raw, uploaded.name)
            st.session_state.df = df
            st.session_state.file_key = key
            st.session_state.dashboard = generate_dashboard(df)
            st.session_state.filters = {}
        except (ValueError, OSError, ImportError) as exc:
            st.error(str(exc))
            st.stop()
df = st.session_state.df
if df is None:
    st.info("Mulai dengan mengunggah file, atau gunakan dataset contoh di bawah.")
    sample = Path(__file__).parent / "sample_data" / "sample_sales.csv"
    if st.button("Muat dataset contoh"):
        st.session_state.df = pd.read_csv(sample)
        st.session_state.file_key = "sample_sales.csv"
        st.session_state.dashboard = generate_dashboard(st.session_state.df)
        st.rerun()
    st.markdown("**Format yang didukung:** CSV, XLSX, XLS. Maksimum default 50 MB.")
    st.stop()

profile, quality = profile_dataset(df)
nav = st.sidebar.radio("Navigasi", ["Overview", "Data Explorer", "Chart Builder", "Filters", "Layout", "Export"], index=0)
filtered = apply_filters(df, st.session_state.filters)
profile_filtered, _ = profile_dataset(filtered)
dashboard = st.session_state.dashboard or generate_dashboard(df)

if nav == "Overview":
    st.subheader(dashboard.get("dashboard_name", "Dashboard Otomatis"))
    st.caption(f"Sumber: {uploaded.name if uploaded else 'sample_sales.csv'}")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Baris", f"{len(filtered):,}")
    c2.metric("Kolom", f"{len(filtered.columns):,}")
    c3.metric("Sel kosong", f"{int(filtered.isna().sum().sum()):,}")
    c4.metric("Baris duplikat", f"{int(filtered.duplicated().sum()):,}")
    items = [x for x in normalize_layout(dashboard.get("charts", [])) if x.get("visible", True)]
    ncols = max(1, min(3, int(dashboard.get("layout", {}).get("columns", 2))))
    for start in range(0, len(items), ncols):
        cols = st.columns(ncols)
        for j, item in enumerate(items[start:start+ncols]):
            with cols[j]:
                st.markdown(f"**{item.get('title','Visualisasi')}**")
                if item.get("chart_type") == "table":
                    st.dataframe(filtered.head(100), use_container_width=True, hide_index=True)
                else:
                    try:
                        fig = build_chart(filtered, item)
                        if fig is not None: st.plotly_chart(fig, use_container_width=True)
                    except (ValueError, KeyError, TypeError) as exc:
                        st.warning(f"Visualisasi ini perlu disesuaikan: {exc}")
    st.subheader("Insight awal")
    for insight in generate_insights(filtered, profile_filtered): st.write("• " + insight)
    st.caption("Insight bersifat deskriptif. Korelasi tidak menunjukkan sebab-akibat.")

elif nav == "Data Explorer":
    st.subheader("Data Explorer")
    st.write(f"**{uploaded.name if uploaded else 'sample_sales.csv'}** · {uploaded.size:,} byte" if uploaded else "**sample_sales.csv**")
    st.dataframe(df.head(1000), use_container_width=True, hide_index=True)
    st.subheader("Profil kolom")
    st.dataframe(profile, use_container_width=True, hide_index=True)
    st.subheader("Kualitas data")
    a,b,c = st.columns(3)
    a.metric("Sel kosong", f"{quality['sel_kosong']:,}", f"{quality['persen_sel_kosong']}% dari seluruh sel")
    b.metric("Baris duplikat", f"{quality['baris_duplikat']:,}")
    c.metric("Kolom", quality["kolom"])
    st.subheader("Statistik numerik")
    st.dataframe(numeric_summary(df), use_container_width=True, hide_index=True)

elif nav == "Chart Builder":
    st.subheader("Chart Builder")
    charts = dashboard.setdefault("charts", [])
    with st.form("new_chart"):
        title = st.text_input("Judul grafik", "Grafik baru")
        kind = st.selectbox("Jenis grafik", sorted(VALID_CHARTS - {"table"}))
        cols = list(df.columns)
        x = st.selectbox("Kolom X", ["(tidak ada)"] + cols)
        y = st.selectbox("Kolom Y", ["(tidak ada)"] + cols)
        color = st.selectbox("Warna / grouping", ["(tidak ada)"] + cols)
        agg = st.selectbox("Agregasi", ["sum","mean","median","count","min","max"])
        limit = st.slider("Maksimum kategori", 3, 50, 20)
        xlab = st.text_input("Label sumbu X")
        ylab = st.text_input("Label sumbu Y")
        submitted = st.form_submit_button("Tambah grafik")
    if submitted:
        cfg = {"title":title, "chart_type":kind, "x":None if x=="(tidak ada)" else x,
               "y":None if y=="(tidak ada)" else y, "color":None if color=="(tidak ada)" else color,
               "aggregation":agg, "category_limit":limit, "x_label":xlab, "y_label":ylab, "visible":True}
        try:
            fig = build_chart(filtered, cfg)
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(filtered.head(100))
            charts.append(cfg)
            st.session_state.dashboard = dashboard
            st.success("Grafik ditambahkan ke dashboard.")
        except (ValueError, KeyError, TypeError) as exc:
            st.error(f"Konfigurasi belum valid: {exc}")
    st.divider()
    st.markdown("**Grafik saat ini**")
    for i, item in enumerate(charts):
        with st.expander(f"{i+1}. {item.get('title','Visualisasi')} · {item.get('chart_type')}"):
            st.json(item)
            if item.get("chart_type") == "table":
                st.dataframe(filtered.head(100))
            else:
                try:
                    fig = build_chart(filtered, item)
                    if fig is not None: st.plotly_chart(fig, use_container_width=True)
                except (ValueError, KeyError, TypeError) as exc: st.warning(str(exc))
            if st.button("Hapus grafik", key=f"delete_{i}"):
                charts.pop(i); st.session_state.dashboard = dashboard; st.rerun()

elif nav == "Filters":
    st.subheader("Filter interaktif")
    st.caption("Filter diterapkan konsisten pada KPI, grafik, insight, dan ekspor data hasil filter.")
    with st.form("filters_form"):
        new_filters = {}
        for col in df.columns:
            s = df[col]
            if pd.api.types.is_numeric_dtype(s) and s.notna().any():
                lo, hi = float(s.min()), float(s.max())
                chosen = st.slider(f"{col} · rentang", min_value=lo, max_value=hi, value=(lo,hi), key=f"range_{col}")
                include_missing = st.checkbox(f"Sertakan nilai kosong · {col}", key=f"missing_num_{col}")
                if chosen != (lo,hi) or include_missing:
                    new_filters[col] = {"type":"numeric","min":chosen[0],"max":chosen[1],"include_missing":include_missing}
            elif pd.api.types.is_datetime64_any_dtype(s):
                dates = pd.to_datetime(s, errors="coerce").dropna()
                if len(dates):
                    chosen = st.date_input(f"{col} · rentang tanggal", value=(dates.min().date(), dates.max().date()), key=f"date_{col}")
                    if isinstance(chosen, tuple) and len(chosen)==2:
                        new_filters[col] = {"type":"date","start":str(chosen[0]),"end":str(chosen[1])}
            elif s.nunique(dropna=True) <= 200:
                vals = sorted(s.dropna().astype(str).unique().tolist())
                opts = (["(Kosong)"] if s.isna().any() else []) + vals
                chosen = st.multiselect(f"{col} · kategori", opts, default=opts, key=f"cat_{col}")
                if len(chosen) != len(opts): new_filters[col] = {"type":"category","values":chosen}
            else:
                query = st.text_input(f"{col} · cari teks", key=f"text_{col}")
                if query: new_filters[col] = {"type":"text","query":query}
        apply = st.form_submit_button("Terapkan filter")
    if apply:
        st.session_state.filters = new_filters
        st.success("Filter diterapkan.")
        st.rerun()
    if st.button("Reset semua filter"):
        st.session_state.filters = {}; st.rerun()
    st.write(f"Baris setelah filter: **{len(filtered):,}** dari {len(df):,}")

elif nav == "Layout":
    st.subheader("Pengaturan layout")
    st.caption("Gunakan tombol naik/turun untuk mengurutkan elemen; drag-and-drop belum termasuk versi ini.")
    cols = st.select_slider("Jumlah kolom dashboard", options=[1,2,3], value=int(dashboard.get("layout",{}).get("columns",2)))
    dashboard.setdefault("layout", {})["columns"] = cols
    charts = dashboard.setdefault("charts", [])
    for i, item in enumerate(charts):
        c1,c2,c3,c4 = st.columns([5,1,1,2])
        with c1:
            visible = st.checkbox(item.get("title","Visualisasi"), value=item.get("visible",True), key=f"vis_{i}")
            item["visible"] = visible
        with c2:
            if st.button("↑", key=f"up_{i}", disabled=i==0):
                dashboard["charts"] = move_item(charts,i,-1); st.session_state.dashboard=dashboard; st.rerun()
        with c3:
            if st.button("↓", key=f"down_{i}", disabled=i==len(charts)-1):
                dashboard["charts"] = move_item(charts,i,1); st.session_state.dashboard=dashboard; st.rerun()
        with c4: st.caption(item.get("chart_type",""))
    st.session_state.dashboard = dashboard
    st.success("Perubahan layout disimpan pada sesi dan akan ikut ekspor konfigurasi.")

elif nav == "Export":
    st.subheader("Ekspor dan penyimpanan konfigurasi")
    dashboard["dashboard_name"] = st.text_input("Nama dashboard", dashboard.get("dashboard_name","Dashboard Otomatis"))
    st.download_button("Unduh data hasil filter (CSV)", dataframe_csv(filtered), file_name="autodash_data_filtered.csv", mime="text/csv")
    st.download_button("Unduh ringkasan statistik (CSV)", dataframe_csv(numeric_summary(filtered)), file_name="autodash_ringkasan.csv", mime="text/csv")
    config_bytes = json.dumps(dashboard, ensure_ascii=False, indent=2, default=str).encode("utf-8")
    st.download_button("Unduh konfigurasi dashboard (JSON)", config_bytes, file_name="autodash_config.json", mime="application/json")
    st.download_button("Unduh laporan HTML", html_report(dashboard["dashboard_name"], filtered, generate_insights(filtered, profile_filtered), dashboard), file_name="autodash_laporan.html", mime="text/html")
    st.divider()
    st.markdown("**Impor konfigurasi JSON**")
    config_file = st.file_uploader("Pilih file konfigurasi", type=["json"], key="config_upload")
    if config_file is not None:
        try:
            imported = load_config(config_file.getvalue().decode("utf-8"), list(df.columns), from_text=True)
            if st.button("Terapkan konfigurasi impor"):
                st.session_state.dashboard = imported
                st.success("Konfigurasi berhasil diimpor.")
                st.rerun()
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            st.error(f"Konfigurasi tidak valid: {exc}")
