import streamlit as st
import plotly.express as px
import pandas as pd

from utils.analytics import get_analytics

st.set_page_config(page_title="Upset Analysis", layout="wide")
st.title("Upset Analysis")
st.caption("Historical upset patterns among teams participating in World Cup 2026")

data = get_analytics()
matches = data["matches"]
elo = data["elo"]

# Compute pre-match Elo for each historical match
upsets = []
for _, m in matches.iterrows():
    h, a = m["home_team"], m["away_team"]
    if h not in elo.ratings or a not in elo.ratings:
        continue
    p_home = elo.win_probability(h, a)
    favorite = h if p_home >= 0.5 else a
    underdog = a if favorite == h else h
    fav_prob = max(p_home, 1 - p_home)
    hs, as_ = m.get("home_score", 0), m.get("away_score", 0)
    if hs == as_:
        continue
    winner = h if hs > as_ else a
    if fav_prob >= 0.6 and winner == underdog:
        upsets.append({
            "year": m["Year"],
            "favorite": favorite,
            "underdog": underdog,
            "winner": winner,
            "round": m.get("Round", ""),
        })

upset_df = pd.DataFrame(upsets)
teams_2026 = set(data["power_rankings"]["team"])

if not upset_df.empty:
    st.subheader("Historical Upsets Involving 2026 Teams")
    relevant = upset_df[
        upset_df["underdog"].isin(teams_2026) | upset_df["favorite"].isin(teams_2026)
    ]
    underdog_counts = (
        relevant[relevant["underdog"].isin(teams_2026)]
        .groupby("underdog")
        .size()
        .reset_index(name="upset_wins")
        .sort_values("upset_wins", ascending=False)
    )
    if not underdog_counts.empty:
        fig = px.bar(
            underdog_counts.head(15),
            x="upset_wins",
            y="underdog",
            orientation="h",
            title="2026 Teams — Historical Upset Wins (as underdog)",
            labels={"underdog": "Team", "upset_wins": "Upset Wins"},
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(relevant.tail(30), hide_index=True, use_container_width=True)
else:
    st.info("No upset data computed.")
