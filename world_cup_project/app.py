import streamlit as st

st.set_page_config(
    page_title="FIFA WC 2026 Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("FIFA World Cup 2026 Analytics Platform")
st.markdown("Navigate using the **sidebar** to explore modules.")
st.page_link("pages/Home.py", label="Go to Home →", icon="🏠")
