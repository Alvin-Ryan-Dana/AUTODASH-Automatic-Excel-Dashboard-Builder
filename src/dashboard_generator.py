"""Build initial dashboard config and render helper."""
from .chart_recommender import recommend_charts

def generate_dashboard(df, limit: int = 6) -> dict:
    """Generate a portable dashboard configuration from dataset characteristics."""
    return {"dashboard_name": "Dashboard Otomatis", "version": 1,
            "charts": recommend_charts(df, limit=limit),
            "layout": {"columns": 2}, "default_filters": {}}
