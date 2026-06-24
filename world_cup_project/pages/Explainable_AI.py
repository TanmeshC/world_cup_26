import streamlit as st
import plotly.express as px

from utils.analytics import get_analytics
from models.match_predictor import MatchPredictor

st.set_page_config(page_title="Explainable AI", layout="wide")
st.title("Explainable AI — Match Predictions")
st.caption("Feature importance and SHAP-style explanations for the match prediction model")

data = get_analytics()
features = data["engineer"].build_match_features()
predictor = MatchPredictor(features).train()

st.subheader("Global Feature Importance")
importance = predictor.get_feature_importance()
fig = px.bar(
    importance,
    x="importance",
    y="feature",
    orientation="h",
    title="Which features matter most for predicting match outcomes?",
    color="importance",
    color_continuous_scale="Purples",
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
**How to interpret:**
- **Elo diff** — Relative team strength is the strongest signal
- **Win rate / goal diff** — Historical World Cup performance patterns
- **Home Elo / Away Elo** — Absolute strength levels

All features are derived from 1930–2022 data. Predictions apply only to 2026-qualified teams.
""")

try:
    import shap
    st.subheader("SHAP Summary (sample)")
    df = features.dropna(subset=importance["feature"].tolist() + ["home_won"])
    sample = df.sample(min(200, len(df)), random_state=42)
    X = sample[importance["feature"].tolist()]
    explainer = shap.TreeExplainer(predictor.model)
    shap_values = explainer.shap_values(X)
    st.pyplot(shap.summary_plot(shap_values, X, show=False), clear_figure=True)
except ImportError:
    st.info("Install `shap` for full SHAP visualizations. Feature importance shown above.")
except Exception as e:
    st.warning(f"SHAP plot unavailable: {e}")
