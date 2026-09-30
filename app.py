import streamlit as st

st.set_page_config(
    page_title="Bond Portfolio Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Global CSS ----------
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

    .hero-banner {
        background: #111111;
        border-bottom: 2px solid #ff6600;
        padding: 12px 18px;
        margin-bottom: 24px;
    }

    .hero-title {
        color: #ff6600;
        font-size: 28px;
        font-weight: bold;
        letter-spacing: 2px;
        font-family: 'Courier New', monospace;
    }

    .card {
        background-color: #111111;
        padding: 18px;
        border: 1px solid #333333;
        border-radius: 10px;
        min-height: 180px;
    }

    .card h3 {
        color: #ff6600;
        margin-bottom: 10px;
    }

    .muted {
        color: #bfbfbf;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">⬡ BOND PORTFOLIO ANALYZER</div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "Application Streamlit d’analyse d’obligations souveraines européennes (EGB) "
    "et de portefeuilles obligataires, avec une interface inspirée des terminaux de marché."
)

st.divider()

# ---------- Navigation cards ----------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
        <h3>📋 Single EGB Analyzer</h3>
        <p class="muted">
            Analyse d’une obligation souveraine : prix, yield, coupon, accrued interest,
            duration, convexity et cash flows.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Single_EGB_Analyzer.py", label="Ouvrir", icon="📋")

with col2:
    st.markdown("""
    <div class="card">
        <h3>📊 EGB Portfolio</h3>
        <p class="muted">
            Analyse d’un portefeuille : market value, poids, duration agrégée,
            DV01/PV01, répartition par pays et maturité.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_EGB_Portfolio.py", label="Ouvrir", icon="📊")

with col3:
    st.markdown("""
    <div class="card">
        <h3>🌍 Curve Analysis</h3>
        <p class="muted">
            Visualisation de la courbe des taux, analyse de spreads souverains
            et comparaison relative value.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_Curve_Analysis.py", label="Ouvrir", icon="🌍")

st.divider()

st.subheader("Fonctionnalités cibles")
st.markdown("""
- Analyse d’une obligation EGB
- Import CSV / Excel d’un portefeuille
- KPIs de risque et de valorisation
- Courbe de taux et spreads vs Bund
- Interface sombre type terminal de marché
""")
