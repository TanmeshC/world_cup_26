import streamlit as st
import plotly.express as px

from utils.analytics import get_analytics
from utils.qualified_teams_2026 import get_qualified_teams

st.set_page_config(page_title="Team Explorer", layout="wide")
st.title("2026 Team Explorer")

data = get_analytics()
teams = get_qualified_teams()
team = st.selectbox("Select a 2026 team", teams)

matches = data["matches"]
team_matches = matches[
    (matches["home_team"] == team) | (matches["away_team"] == team)
].sort_values("Year")

stats = data["engineer"].build_team_statistics()
team_stats = stats[stats["team"] == team].iloc[0]
elo_row = data["elo"].get_2026_ratings()
elo_val = elo_row.loc[elo_row["team"] == team, "elo"].values
power_row = data["power_rankings"]
power_val = power_row.loc[power_row["team"] == team]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("WC Matches", int(team_stats["matches"]))
c2.metric("WC Wins", int(team_stats["wins"]))
c3.metric("Goal Diff", int(team_stats["goal_diff"]))
c4.metric("Elo", f"{elo_val[0]:.0f}" if len(elo_val) else "N/A")
c5.metric("Power Rank", int(power_val["rank"].values[0]) if len(power_val) else "N/A")

st.subheader("World Cup Appearances")
appearances = team_matches.groupby("Year").size().reset_index(name="matches")
fig = px.bar(appearances, x="Year", y="matches", title=f"{team} — Matches per Tournament")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Match History")
display_cols = ["Year", "Round", "Date", "home_team", "home_score", "away_score", "away_team"]
history = team_matches.copy()
history["perspective"] = history.apply(
    lambda r: "Home" if r["home_team"] == team else "Away", axis=1
)
st.dataframe(
    history[display_cols + ["perspective"]].tail(20),
    hide_index=True,
    use_container_width=True,
)
