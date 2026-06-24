import streamlit as st
import plotly.express as px

from utils.analytics import get_analytics
from models.match_predictor import MatchPredictor

st.set_page_config(page_title="Match Predictor", layout="wide")
st.title("Match Predictor")
st.caption("Gradient Boosting model trained on 1930–2022 WC matches · Predicts 2026 matchups only")

data = get_analytics()
features = data["engineer"].build_match_features()
predictor = MatchPredictor(features).train()

st.sidebar.metric("CV Accuracy (5-fold)", f"{predictor.cv_accuracy:.1%}")

teams = data["power_rankings"]["team"].tolist()
c1, c2 = st.columns(2)
with c1:
    home = st.selectbox("Home Team", teams, index=teams.index("Argentina") if "Argentina" in teams else 0)
with c2:
    away = st.selectbox("Away Team", teams, index=teams.index("Brazil") if "Brazil" in teams else 1)

if home != away:
    result = predictor.predict_match(home, away, data["elo"], data["engineer"])
    col1, col2, col3 = st.columns(3)
    col1.metric(home, f"{result['home_win_prob']:.1%}")
    col2.metric("Predicted Winner", result["predicted_winner"])
    col3.metric(away, f"{result['away_win_prob']:.1%}")

    fig = px.bar(
        x=[home, away],
        y=[result["home_win_prob"], result["away_win_prob"]],
        color=[home, away],
        labels={"x": "Team", "y": "Win Probability"},
        title="Match Outcome Probabilities",
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Feature Importance")
importance = predictor.get_feature_importance()
fig_imp = px.bar(importance, x="importance", y="feature", orientation="h",
                 title="What drives predictions?")
st.plotly_chart(fig_imp, use_container_width=True)
