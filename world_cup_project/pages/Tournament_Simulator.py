import streamlit as st
import plotly.express as px

from utils.analytics import get_analytics
from models.tournament_simulator import TournamentSimulator

st.set_page_config(page_title="Tournament Simulator", layout="wide")
st.title("Tournament Simulator")
st.caption("Simulate knockout brackets for 2026-qualified teams")

data = get_analytics()
sim = TournamentSimulator(data["elo"], n_simulations=1)

if st.button("Run Single Tournament Simulation", type="primary"):
    result = sim.simulate_with_stages()
    st.success(f"🏆 Champion: **{result['champion']}**")
    for stage, info in result["stages"].items():
        with st.expander(stage):
            st.write("Teams:", ", ".join(info["teams"]))
            st.write("Advancing:", ", ".join(info["winners"]))
            if info["upsets"]:
                st.write("Upsets:", info["upsets"])

st.subheader("Upset Frequency (1,000 simulations)")
with st.spinner("Simulating..."):
    upsets = sim.upset_frequency(n_sims=1000)

if not upsets.empty:
    fig = px.bar(
        upsets.head(15),
        x="rate",
        y="team",
        orientation="h",
        title="Teams Most Likely to Pull Off Upsets",
        labels={"rate": "Upset Win Rate"},
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)
