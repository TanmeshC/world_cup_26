import streamlit as st
import plotly.express as px

from utils.analytics import get_analytics
from utils.qualified_teams_2026 import get_qualified_teams

st.set_page_config(page_title="Historical Research", layout="wide")
st.title("Historical Research")
st.caption("World Cup trends from 1930–2022, contextualized for 2026 participants")

data = get_analytics()
matches = data["matches"]
teams_2026 = set(get_qualified_teams())

st.subheader("Goals per Tournament")
goals_by_year = matches.groupby("Year").agg(
    total_goals=("home_score", "sum"),
    matches=("home_score", "count"),
).reset_index()
goals_by_year["goals_per_match"] = goals_by_year["total_goals"] / goals_by_year["matches"] * 2
fig = px.line(goals_by_year, x="Year", y="goals_per_match", markers=True,
              title="Average Goals per Match by Tournament")
st.plotly_chart(fig, use_container_width=True)

st.subheader("2026 Teams — Historical WC Experience")
stats = data["engineer"].build_team_statistics()
stats_2026 = stats[stats["team"].isin(teams_2026)].sort_values("matches", ascending=False)
fig2 = px.bar(
    stats_2026.head(20),
    x="matches",
    y="team",
    orientation="h",
    title="Most Experienced 2026 Teams (WC Matches)",
    labels={"matches": "World Cup Matches"},
)
fig2.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig2, use_container_width=True)

st.subheader("First-Time vs Returning Participants")
first_timers = stats_2026[stats_2026["matches"] == 0]["team"].tolist()
returning = stats_2026[stats_2026["matches"] > 0]["team"].tolist()
col1, col2 = st.columns(2)
col1.metric("Returning Teams", len(returning))
col2.metric("No Prior WC Matches in Dataset", len(first_timers))
if first_timers:
    st.write("Teams with no historical WC match data:", ", ".join(sorted(first_timers)))
