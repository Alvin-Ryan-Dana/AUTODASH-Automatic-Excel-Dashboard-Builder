import pandas as pd
from src.chart_recommender import recommend_charts

def test_recommends_numeric_and_category_charts():
    df = pd.DataFrame({"group":["a","b","a"],"amount":[2,3,5],"other":[1,4,8]})
    charts = recommend_charts(df)
    assert charts
    assert any(x["chart_type"] == "histogram" for x in charts)
    assert any(x["chart_type"] == "scatter" for x in charts)

def test_empty_dataset():
    assert recommend_charts(pd.DataFrame()) == []
