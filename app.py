import streamlit as st
import yfinance as yf
import pandas as pd

# --- CONFIGURATION GLOBALE ---
st.set_page_config(
    page_title="Quant Finance Portfolio",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS PERSONNALISÉ (Minimaliste & Épuré) ---
st.markdown("""
    <style>
    .stButton>button {
        border-radius: 6px;
        height: 3em;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
        border: 1px solid #E5E7EB;
        background-color: transparent;
    }
    .stButton>button:hover {
        border-color: #0068C9;
        color: #0068C9;
        transform: translateY(-2px);
    }
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTION D'EXTRACTION DES DONNÉES (Robuste & Cachée) ---
@st.cache_data(ttl=300, show_spinner=False)
def fetch_market_overview():
    """Récupère les indicateurs de marché avec gestion d'erreurs."""
    tickers_dict = {
        "S&P 500": "^GSPC", 
        "NASDAQ": "^IXIC", 
        "VIX (Volatility)": "^VIX", 
        "US 10Y Yield": "^TNX"
    }
    market_data = {}
    
    try:
        # Téléchargement groupé pour la performance
        tickers_str = " ".join(tickers_dict.values())
        df = yf.download(tickers_str, period="5d", progress=False)["Close"]
        
        for name, ticker in tickers_dict.items():
            if ticker in df.columns and len(df[ticker].dropna()) >= 2:
                series = df[ticker].dropna()
                current = series.iloc[-1]
                prev = series.iloc[-2]
                delta = current - prev
                delta_pct = (delta / prev) * 100
                market_data[name] = {"current": current, "delta": delta, "delta_pct": delta_pct}
            else:
                market_data[name] = None
        return market_data
    except Exception:
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    st.info("Utilisez les modules ci-contre pour explorer mes travaux en ingénierie financière.")
    st.divider()
    st.caption("Version 1.1.0 - 2026 | System: Online")

# --- HERO SECTION ---
st.title("📈 Quantitative Finance & Risk Analysis")
st.subheader("Bridging Financial Theory and Data Engineering")

st.markdown("""
Welcome! This platform is a curated collection of financial models and interactive tools.  
It reflects my journey in exploring market mechanics, credit risk, and real-time intelligence through code.
""")

st.write("") # Espacement

# --- LIVE MARKET DASHBOARD ---
market_data = fetch_market_overview()

if market_data:
    cols = st.columns(4)
    metrics_config = [
        ("S&P 500", "", "normal"),
        ("NASDAQ", "", "normal"),
        ("VIX (Volatility)", " pts", "inverse"), # inverse : baisse = vert
        ("US 10Y Yield", "%", "inverse")         # inverse : baisse = vert (généralement perçu comme détente)
    ]
    
    for col, (name, suffix, color_behavior) in zip(cols, metrics_config):
        data = market_data.get(name)
        with col:
            if data:
                # Formatage spécifique selon l'indicateur
                val_format = f"{data['current']:,.2f}{suffix}"
                delta_format = f"{data['delta']:+.2f} ({data['delta_pct']:+.2f}%)"
                st.metric(
                    label=name, 
                    value=val_format, 
                    delta=delta_format, 
                    delta_color=color_behavior
                )
            else:
                st.metric(label=name, value="N/A", delta="N/A")
else:
    st.warning("⚠️ Market data API is currently unavailable. Displaying cached static interfaces.")

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
    "Data Stack": "Python (Pandas, NumPy, SciPy), REST APIs, YFinance.",
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
