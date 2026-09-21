import streamlit as st

st.set_page_config(
    page_title="Bond Portfolio Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS Bloomberg global ───────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background-color: #0a0a0a;
        color: #e0e0e0;
        font-family: 'Courier New', monospace;
    }
    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #ff6600;
    }
</style>
""", unsafe_allow_html=True)

# ── Page d'accueil ─────────────────────────────────────────
st.markdown("""
<div style="background:#111;border-bottom:2px solid #ff6600;
            padding:10px 16px;margin-bottom:24px;">
  <span style="color:#ff6600;font-size:24px;font-weight:bold;
               letter-spacing:3px;font-family:'Courier New';">
    ⬡ BOND PORTFOLIO ANALYZER
  </span>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📋 Portfolio Manager
    Ajoutez, importez et gérez vos obligations
    """)
    st.page_link("pages/01__Portfolio.py", label="➡️ Ouvrir", icon="📋")

with col2:
    st.markdown("""
    ### 📊 Dashboard
    Vue d'ensemble et KPIs du portefeuille
    """)
    st.page_link("pages/02__Dashboard.py", label="➡️ Ouvrir", icon="📊")

with col3:
    st.markdown("""
    ### 🌍 Market View
    Données de marché et courbe des taux
    """)
    st.page_link("pages/03__Market_view.py", label="➡️ Ouvrir", icon="🌍")
