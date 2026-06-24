import streamlit as st
import plotly.express as px

from utils.analytics import get_analytics

st.set_page_config(page_title="Power Rankings", layout="wide")
st.title("2026 World Cup Power Rankings")
st.caption("Composite index: 40% Elo · 30% FIFA Points · 15% WC Wins · 10% WC Appearances · 5% Recent Form")

data = get_analytics()
rankings = data["power_rankings"]

fig = px.scatter(
    rankings,
    x="elo",
    y="fifa_points",
    size="power_index",
    color="power_index",
    hover_name="team",
    color_continuous_scale="Viridis",
    labels={"elo": "Elo Rating", "fifa_points": "FIFA Ranking Points"},
    title="Power Index Landscape",
)
st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    rankings[["rank", "team", "power_index", "elo", "fifa_points", "wc_wins", "wc_matches", "recent_points"]]
    .round(2),
    hide_index=True,
    use_container_width=True,
)

selected = st.selectbox("Team breakdown", rankings["team"])
row = rankings[rankings["team"] == selected].iloc[0]
components = {
    "Elo (40%)": row["elo_norm"] * 40,
    "FIFA Points (30%)": row["fifa_norm"] * 30,
    "WC Wins (15%)": row["wc_wins_norm"] * 15,
    "WC Appearances (10%)": row["wc_matches_norm"] * 10,
    "Recent Form (5%)": row["form_norm"] * 5,
}
fig_bar = px.bar(
    x=list(components.values()),
    y=list(components.keys()),
    orientation="h",
    title=f"{selected} — Power Index Components",
    labels={"x": "Contribution", "y": "Component"},
)
st.plotly_chart(fig_bar, use_container_width=True)
