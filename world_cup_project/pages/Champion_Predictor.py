import streamlit as st
import plotly.express as px

from utils.analytics import get_analytics
from models.champion_predictor import ChampionPredictor

st.set_page_config(page_title="Champion Predictor", layout="wide")
st.title("2026 World Cup Champion Predictor")
st.caption("Monte Carlo simulation using Elo-based knockout bracket · 2026 teams only")

data = get_analytics()
n_sims = st.sidebar.slider("Simulations", 1000, 50000, 10000, step=1000)

with st.spinner(f"Running {n_sims:,} simulations..."):
    predictor = ChampionPredictor(data["elo"], n_simulations=n_sims)
    results = predictor.run_simulations()

top15 = results.head(15)
fig = px.bar(
    top15,
    x="probability",
    y="team",
    orientation="h",
    color="probability",
    color_continuous_scale="Reds",
    labels={"probability": "Championship Probability"},
    title="Championship Probabilities",
)
fig.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    results.assign(probability_pct=(results["probability"] * 100).round(2))
    [["team", "probability_pct", "championships"]]
    .rename(columns={"probability_pct": "probability (%)"}),
    hide_index=True,
    use_container_width=True,
)
