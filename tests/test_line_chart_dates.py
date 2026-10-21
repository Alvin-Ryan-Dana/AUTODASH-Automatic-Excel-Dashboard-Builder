import pandas as pd

from src.chart_builder import build_chart


def make_line(df, aggregation="sum"):
    return build_chart(df, {
        "chart_type": "line", "x": "Tanggal", "y": "Nilai",
        "aggregation": aggregation, "title": "Uji tanggal",
    })


def test_line_chart_sorts_unsorted_dates_chronologically_and_keeps_source_unchanged():
    df = pd.DataFrame({
        "Tanggal": ["2024-01-03", "2024-01-01", "2024-01-10", "2024-01-02"],
        "Nilai": [30, 10, 100, 20],
    })
    original = df.copy(deep=True)
    fig = make_line(df)
    assert list(pd.to_datetime(fig.data[0].x)) == list(pd.to_datetime([
        "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-10"
    ]))
    assert df.equals(original)
    assert fig.layout.xaxis.type == "date" or fig.layout.xaxis.type is None


def test_duplicate_dates_are_aggregated_using_selected_aggregation():
    df = pd.DataFrame({
        "Tanggal": ["03/01/2024", "01/01/2024", "03/01/2024", "02/01/2024"],
        "Nilai": [30, 10, 5, 20],
    })
    fig = make_line(df, aggregation="sum")
    dates = list(pd.to_datetime(fig.data[0].x))
    values = list(fig.data[0].y)
    assert dates == list(pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]))
    assert values == [10, 20, 35]


def test_indonesian_month_names_are_parsed():
    df = pd.DataFrame({
        "Tanggal": ["3 Januari 2024", "1 Januari 2024", "2 Januari 2024"],
        "Nilai": [3, 1, 2],
    })
    fig = make_line(df)
    assert list(pd.to_datetime(fig.data[0].x)) == list(pd.to_datetime([
        "2024-01-01", "2024-01-02", "2024-01-03"
    ]))


def test_unrecognizable_category_is_not_silently_converted():
    df = pd.DataFrame({"Tanggal": ["alpha", "gamma", "beta"], "Nilai": [1, 3, 2]})
    fig = make_line(df)
    assert list(fig.data[0].x) == ["alpha", "beta", "gamma"]


def test_existing_excel_datetime_column_stays_datetime_on_plotly_axis():
    df = pd.DataFrame({
        "Tanggal": pd.to_datetime(["2024-01-03", "2024-01-01", "2024-01-02"]),
        "Nilai": [3, 1, 2],
    })
    fig = make_line(df)
    assert fig.layout.xaxis.type == "date"
    assert list(pd.to_datetime(fig.data[0].x)) == list(pd.to_datetime([
        "2024-01-01", "2024-01-02", "2024-01-03"
    ]))


def test_mixed_recognizable_date_formats_are_parsed():
    df = pd.DataFrame({
        "Tanggal": ["2024-01-03", "01/01/2024", "2 Januari 2024"],
        "Nilai": [3, 1, 2],
    })
    fig = make_line(df)
    assert list(pd.to_datetime(fig.data[0].x)) == list(pd.to_datetime([
        "2024-01-01", "2024-01-02", "2024-01-03"
    ]))
