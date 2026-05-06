import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURATION GLOBALE ---
st.set_page_config(
    page_title="Quant Finance Portfolio",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS PERSONNALISÉ (Style Morningstar) ---
st.markdown("""
    <style>
    /* Clean UI type Morningstar */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
        color: #555;
    }
    .stTabs [aria-selected="true"] {
        color: #000 !important;
        border-bottom: 2px solid #0068C9 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS DATA & GRAPH ---
@st.cache_data(ttl=300, show_spinner=False)
def fetch_market_history(tickers_dict):
    """Récupère l'historique sur 1 mois pour calculer les deltas et tracer les courbes."""
    market_data = {}
    # Extraction de tous les tickers valides
    valid_tickers = [t for t in tickers_dict.values() if t]
    
    try:
        df = yf.download(" ".join(valid_tickers), period="1mo", progress=False)["Close"]
        
        # Si un seul ticker est demandé, yfinance renvoie une Series au lieu d'un DataFrame multi-colonnes
        if isinstance(df, pd.Series):
            df = df.to_frame(name=valid_tickers[0])

        for name, ticker in tickers_dict.items():
            if ticker and ticker in df.columns and len(df[ticker].dropna()) >= 2:
                series = df[ticker].dropna()
                current = series.iloc[-1]
                prev = series.iloc[-2]
                delta = current - prev
                delta_pct = (delta / prev) * 100
                market_data[name] = {
                    "current": current, 
                    "delta": delta, 
                    "delta_pct": delta_pct,
                    "history": series
                }
            else:
                market_data[name] = None
        return market_data
    except Exception as e:
        return {}

def create_sparkline(series, color_behavior="normal"):
    """Génère un mini-graphique Plotly épuré."""
    if series is None or len(series) == 0:
        return go.Figure()

    start_val, end_val = series.iloc[0], series.iloc[-1]
    
    # Détermination de la couleur de la ligne (vert si hausse, rouge si baisse)
    # Si comportement "inverse" (ex: VIX), on inverse les couleurs
    if color_behavior == "inverse":
        line_color = "#00C073" if end_val <= start_val else "#FF2B2B"
    else:
        line_color = "#00C073" if end_val >= start_val else "#FF2B2B"

    fig = go.Figure(go.Scatter(
        x=series.index, 
        y=series.values, 
        mode='lines', 
        line=dict(color=line_color, width=2),
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=40,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False, visible=False),
        showlegend=False
    )
    return fig

# --- DÉFINITION DES CATÉGORIES & TICKERS ---
# Note: FR10, DE10, UK10 ont des tickers erratiques sur YF. Je mets les conventions habituelles mais prépare-toi à du N/A.
categories = {
    "Indices": {
        "CAC 40": "^FCHI",
        "S&P 500": "^GSPC",
        "DAX": "^GDAXI",
        "VIX": "^VIX"
    },
    "Bonds": {
        "US 10Y": "^TNX",
        "FR 10Y": "OAT.PA",     # Instable sur YF
        "DE 10Y": "DBRS.DE",    # Instable sur YF
        "UK 10Y": "IGLT.L"      # ETF proxy pour UK Gilts (faut d'API obligataire pure)
    },
    "Forex": {
        "EUR/USD": "EURUSD=X",
        "USD/JPY": "JPY=X",
        "EUR/GBP": "EURGBP=X",
        "GBP/USD": "GBPUSD=X"
    }
}

# Extraction de tous les tickers pour l'appel API groupé
all_tickers = {}
for cat in categories.values():
    all_tickers.update(cat)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    st.info("Utilisez les modules ci-contre pour explorer mes travaux en ingénierie financière.")
    st.divider()
    st.caption("Version 1.2.0 - 2026 | System: Online")

# --- HERO SECTION ---
st.title("📈 Quantitative Finance & Risk Analysis")
st.subheader("Bridging Financial Theory and Data Engineering")
st.write("")

# --- LIVE MARKET DASHBOARD (MORNINGSTAR STYLE) ---
market_data = fetch_market_history(all_tickers)

if market_data:
    tab1, tab2, tab3 = st.tabs(["📊 Indices", "🏛️ Bonds", "💱 Forex"])
    
    tabs_mapping = zip([tab1, tab2, tab3], categories.keys())
    
    for tab, cat_name in tabs_mapping:
        with tab:
            cols = st.columns(4)
            for col, (asset_name, ticker) in zip(cols, categories[cat_name].items()):
                with col:
                    with st.container(border=True): # Encadrement clean
                        data = market_data.get(asset_name)
                        
                        # Configuration de l'inversion de couleur (ex: VIX ou Taux qui baissent = Positif)
                        color_behavior = "inverse" if asset_name in ["VIX", "US 10Y", "FR 10Y", "DE 10Y", "UK 10Y"] else "normal"
                        
                        if data:
                            suffix = "%" if cat_name == "Bonds" else ""
                            st.metric(
                                label=asset_name, 
                                value=f"{data['current']:,.2f}{suffix}", 
                                delta=f"{data['delta']:+.2f} ({data['delta_pct']:+.2f}%)", 
                                delta_color=color_behavior
                            )
                            # Ajout du Sparkline
                            st.plotly_chart(
                                create_sparkline(data["history"], color_behavior), 
                                use_container_width=True, 
                                config={'displayModeBar': False} # Cache le menu Plotly pour faire propre
                            )
                        else:
                            st.metric(label=asset_name, value="N/A", delta="N/A")
                            st.caption("Données non disponibles via YFinance")
else:
    st.warning("⚠️ Market data API is currently unavailable.")

st.divider()

# --- PROJECT SHOWCASE (Interactive Modules) ---
st.header("🚀 Interactive Modules")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### 🏦 Corporate Credit Risk")
        st.markdown("Evaluates company solvency using the **Altman Z-Score**. Fetches live financial statements to predict potential distress.")
        if st.button("Launch Credit Tool", use_container_width=True, key="btn_credit"):
            st.switch_page("pages/01_Credit_risk_Z-score.py")

with col2:
    with st.container(border=True):
        st.markdown("### 🧮 Option Pricing")
        st.markdown("A **Black-Scholes-Merton** implementation to price European options. Calculates Greeks and visualizes sensitivities.")
        if st.button("Launch Pricing Tool", use_container_width=True, key="btn_option"):
            st.switch_page("pages/02_Option_Pricing.py")

st.write("")

col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.markdown("### 🗞️ Market View") 
        st.markdown("Real-time terminal for **fundamental analysis**. Aggregates news, corporate agendas, and key valuation metrics.")
        if st.button("Launch Intel Tool", use_container_width=True, key="btn_market"):
            st.switch_page("pages/03__Market_view.py")

with col4:
    with st.container(border=True):
        st.markdown("### 🏗️ Work in Progress")
        st.markdown("A new quantitative module is currently under development. Stay tuned for advanced portfolio optimization features.")
        st.button("Coming Soon...", use_container_width=True, disabled=True)

# --- ABOUT ME SECTION ---
st.header("🔍 Why This Portfolio?")
st.markdown("""
I've always believed that finance is best understood when you can **build and break the models yourself**. 
For me, it's not just about reading formulas; it's about seeing how they react to real-time market shifts.
""")

st.divider()

# --- TECHNICAL TOOLKIT ---
st.header("🛠 Technical Toolkit")
skills = {
    "Finance & Math": "Quant Research, Options Greeks, Credit Scoring, Probability.",
    "Data Stack": "Python (Pandas, NumPy, SciPy), REST APIs, Plotly.",
    "Visualization": "Streamlit, Plotly Interactive Charts, LaTeX.",
    "AI Engineering": "LLMs for code optimization, debugging, and rapid prototyping."
}

cols = st.columns(4)
for i, (skill, desc) in enumerate(skills.items()):
    with cols[i]:
        st.write(f"**{skill}**")
        st.caption(desc)

# --- CONTACT SECTION ---
st.divider()
st_col1, st_col2, st_col3 = st.columns(3)

with st_col1:
    st.markdown("🔗 [LinkedIn Profile](https://www.linkedin.com/in/anthony-moubarak-1771a7251/)")
with st_col2:
    st.markdown("💻 [GitHub Repository](https://github.com/TonySerenade/Finance_Board)")
with st_col3:
    st.markdown("📫 [Email Me](mailto:anthony.moubarak14@gmail.com)")
