import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.analytics import get_analytics

st.set_page_config(page_title="Elo Dashboard", layout="wide")
st.title("Elo Rating Dashboard")
st.caption("Ratings computed from all World Cup matches (1930–2022) · Displayed for 2026 teams only")

data = get_analytics()
elo = data["elo"]
ratings = elo.get_2026_ratings()

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(
        ratings.head(20),
        x="elo",
        y="team",
        orientation="h",
        color="elo",
        color_continuous_scale="Blues",
        labels={"elo": "Elo Rating", "team": "Team"},
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=600)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top 10")
    st.dataframe(ratings.head(10)[["rank", "team", "elo"]], hide_index=True, use_container_width=True)

st.subheader("Elo Distribution (2026 Teams)")
fig_hist = px.histogram(ratings, x="elo", nbins=20, labels={"elo": "Elo Rating"})
st.plotly_chart(fig_hist, use_container_width=True)

st.subheader("Head-to-Head Elo Comparison")
teams = ratings["team"].tolist()
c1, c2 = st.columns(2)
with c1:
    team_a = st.selectbox("Team A", teams, index=0)
with c2:
    team_b = st.selectbox("Team B", teams, index=1)

if team_a != team_b:
    pred = elo.predict_match(team_a, team_b)
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pred["home_win_prob"] * 100,
        title={"text": f"{team_a} Win %"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#1f77b4"}},
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.write(
        f"**{team_a}** Elo: {pred['home_elo']:.0f} · "
        f"**{team_b}** Elo: {pred['away_elo']:.0f} · "
        f"Elo diff: {pred['elo_diff']:+.0f}"
    )
