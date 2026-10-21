import pandas as pd
from src.filters import apply_filters
from src.validators import validate_chart_config
from src.chart_builder import build_chart
from src.dashboard_storage import save_config, load_config

def test_numeric_and_category_filters():
    df = pd.DataFrame({"n":[1,2,3,None],"c":["a","b","a","b"]})
    got = apply_filters(df, {"n":{"type":"numeric","min":2,"max":3},"c":{"type":"category","values":["a"]}})
    assert got["n"].tolist() == [3.0]

def test_all_rows_filtered():
    df = pd.DataFrame({"n":[1,2]})
    assert apply_filters(df, {"n":{"type":"numeric","min":9,"max":10}}).empty

def test_aggregation_chart():
    df = pd.DataFrame({"c":["a","a","b"],"n":[1,3,10]})
    for agg in ("sum","mean","median","count","min","max"):
        fig = build_chart(df, {"chart_type":"bar","x":"c","y":"n","aggregation":agg})
        assert fig is not None

def test_config_roundtrip_and_invalid(tmp_path):
    cfg = {"dashboard_name":"Test","charts":[{"chart_type":"bar","x":"c","y":"n"}],"layout":{"columns":2}}
    path = tmp_path / "cfg.json"
    save_config(cfg,path)
    assert load_config(path,["c","n"])["dashboard_name"] == "Test"
    try:
        load_config(path,["different"])
    except ValueError:
        pass
    else:
        raise AssertionError("Expected invalid column config")

def test_chart_validation():
    ok, message = validate_chart_config({"chart_type":"bar","x":"missing","y":"n"}, ["n"])
    assert not ok and "tidak ditemukan" in message
