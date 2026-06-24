import streamlit as st
import plotly.express as px

from utils.analytics import get_analytics
from utils.qualified_teams_2026 import get_qualified_teams

st.set_page_config(page_title="WC 2026 Analytics", page_icon="⚽", layout="wide")

st.title("FIFA World Cup 2026 Analytics Platform")
st.markdown(
    """
    **Based on everything that happened in World Cup history (1930–2022),
    what can we learn and predict about the teams participating in FIFA World Cup 2026?**

    This platform uses **all historical World Cup data** for training, Elo calculations,
    feature engineering, and model building — but every ranking, prediction, and dashboard
    is restricted to **2026-qualified teams only**.
    """
)

data = get_analytics()
teams = get_qualified_teams()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Historical Matches", f"{len(data['matches']):,}")
col2.metric("2026 Teams", len(teams))
col3.metric("Tournaments Analyzed", data["matches"]["Year"].nunique())
col4.metric("Top Elo Rating", f"{data['elo'].get_2026_ratings()['elo'].iloc[0]:.0f}")

st.subheader("2026 Power Rankings Preview")
top10 = data["power_rankings"].head(10)
fig = px.bar(
    top10,
    x="power_index",
    y="team",
    orientation="h",
    color="power_index",
    color_continuous_scale="Greens",
    title="Top 10 Power Index (2026 Teams)",
)
fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Platform Modules")
st.markdown(
    """
    | Module | Description |
    |--------|-------------|
    | **Elo Dashboard** | Dynamic Elo ratings from 1930–2022, shown for 2026 teams |
    | **Power Rankings** | Composite index: Elo + FIFA + WC history + form |
    | **Match Predictor** | ML model predicting head-to-head outcomes |
    | **Champion Predictor** | Monte Carlo championship probabilities |
    | **Tournament Simulator** | Full knockout simulation with upset tracking |
    | **Team Explorer** | Deep-dive stats for any 2026 team |
    | **Historical Research** | Statistical trends (context for 2026 teams) |
    | **Upset Analysis** | Underdog win patterns among 2026 participants |
    | **Explainable AI** | SHAP feature importance for match predictions |
    """
)
