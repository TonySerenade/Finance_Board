import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from scipy.stats import norm

# ==========================================
# 1. CONFIGURATION DE LA PAGE & STYLE CSS
# ==========================================
st.set_page_config(
    page_title="SYS > FINANCE BOARD",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injection du CSS façon Terminal Bloomberg
bloomberg_css = """
<style>
    /* Fond noir absolu */
    .stApp { background-color: #000000; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #333333; }
    
    /* Typographie Monospace */
    html, body, [class*="css"] {
        font-family: 'Courier New', Courier, monospace !important;
        color: #E0E0E0 !important;
    }
    
    /* Titres en orange néon */
    h1, h2, h3 { color: #FF9900 !important; text-transform: uppercase; border-bottom: 1px solid #333333; padding-bottom: 5px; }
    
    /* Métriques en vert par défaut */
    [data-testid="stMetricValue"], [data-testid="stMetricDelta"] { color: #00FF00 !important; }
    [data-testid="stMetricDelta"] svg { fill: #00FF00 !important; }
    
    /* Inputs et Boutons */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #111111 !important; color: #FF9900 !important; border: 1px solid #FF9900 !important;
    }
    .stButton>button {
        background-color: #000000; color: #FF9900; border: 1px solid #FF9900; border-radius: 0; width: 100%;
    }
    .stButton>button:hover { background-color: #FF9900; color: #000000; }
    
    /* Séparateurs */
    hr { border-top: 1px dashed #FF9900; }
</style>
"""
st.markdown(bloomberg_css, unsafe_allow_html=True)

# ==========================================
# 2. FONCTIONS DE CALCUL (FINANCE QUANTITATIVE)
# ==========================================

# Fonction Black-Scholes-Merton
def black_scholes(S, K, T, r, sigma, option_type="call"):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1
    
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100 # Divisé par 100 pour %
    
    return price, delta, gamma, vega

# ==========================================
# 3. INTERFACE UTILISATEUR & NAVIGATION
# ==========================================

st.sidebar.markdown("<h2 style='text-align: center; color: #FF9900;'>SYS // MENU</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "COMMANDES :",
    ["1. MARKET INTELLIGENCE", "2. CREDIT RISK (Z-SCORE)", "3. DERIVATIVES PRICING"]
)

st.title(f"SYS > {menu[3:]}")
st.markdown("---")

# ==========================================
# PAGE 1 : MARKET INTELLIGENCE
# ==========================================
if menu == "1. MARKET INTELLIGENCE":
    st.subheader(">> EQUITIES & MACRO DATA")
    
    # Bandeau de cotations rapides
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("SPX Index", "5,123.45", "+12.4")
    col2.metric("EUR/USD Curncy", "1.0854", "-0.0012")
    col3.metric("US 10Y Yield", "4.23%", "+0.05%")
    col4.metric("VIX Index", "14.23", "-0.45")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recherche de Ticker
    ticker = st.text_input(">> ENTER TICKER (ex: AAPL, MSFT, TSLA) :", value="AAPL")
    if st.button("EXECUTE // FETCH DATA"):
        with st.spinner("Fetching data from market..."):
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")
            
            if not hist.empty:
                # Graphique sombre Plotly
                fig = go.Figure(data=[go.Candlestick(x=hist.index,
                                open=hist['Open'], high=hist['High'],
                                low=hist['Low'], close=hist['Close'])])
                fig.update_layout(
                    title=f"{ticker.upper()} - 6 MONTHS CHART",
                    template="plotly_dark",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Courier New", color="#FF9900"),
                    xaxis_rangeslider_visible=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Infos fondamentales
                info = stock.info
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Market Cap:** {info.get('marketCap', 'N/A'):,}")
                c2.write(f"**PE Ratio:** {info.get('trailingPE', 'N/A')}")
                c3.write(f"**Beta:** {info.get('beta', 'N/A')}")
            else:
                st.error("TICKER NOT FOUND.")

# ==========================================
# PAGE 2 : CREDIT RISK (ALTMAN Z-SCORE)
# ==========================================
elif menu == "2. CREDIT RISK (Z-SCORE)":
    st.subheader(">> ALTMAN Z-SCORE CALCULATOR")
    st.write("Évaluation de la solvabilité et du risque de faillite corporative.")
    
    col1, col2 = st.columns(2)
    with col1:
        working_capital = st.number_input("Working Capital ($)", value=50000.0)
        retained_earnings = st.number_input("Retained Earnings ($)", value=20000.0)
        ebit = st.number_input("EBIT ($)", value=15000.0)
    with col2:
        market_value_equity = st.number_input("Market Value of Equity ($)", value=100000.0)
        total_liabilities = st.number_input("Total Liabilities ($)", value=60000.0)
        total_assets = st.number_input("Total Assets ($)", value=120000.0)
        
    if st.button("EXECUTE // COMPUTE Z-SCORE"):
        # Calculs des ratios
        A = working_capital / total_assets
        B = retained_earnings / total_assets
        C = ebit / total_assets
        D = market_value_equity / total_liabilities
        E = (working_capital + retained_earnings) / total_assets # Proxy simplifié pour Sales/Assets si non dispo
        
        z_score = (1.2 * A) + (1.4 * B) + (3.3 * C) + (0.6 * D) + (1.0 * E)
        
        st.markdown("---")
        st.subheader(f">> Z-SCORE: {z_score:.2f}")
        
        if z_score >= 2.99:
            st.success("STATUS: SAFE ZONE (Faible risque de faillite)")
        elif 1.81 <= z_score < 2.99:
            st.warning("STATUS: GREY ZONE (Zone de prudence)")
        else:
            st.error("STATUS: DISTRESS ZONE (Risque élevé de faillite)")

# ==========================================
# PAGE 3 : DERIVATIVES PRICING (BLACK-SCHOLES)
# ==========================================
elif menu == "3. DERIVATIVES PRICING":
    st.subheader(">> BLACK-SCHOLES-MERTON ENGINE")
    
    col1, col2 = st.columns(2)
    with col1:
        S = st.number_input("Spot Price (S)", value=100.0)
        K = st.number_input("Strike Price (K)", value=100.0)
        T = st.number_input("Time to Maturity (Years)", value=1.0)
    with col2:
        r = st.number_input("Risk-Free Rate (r)", value=0.05, format="%.4f")
        sigma = st.number_input("Volatility (σ)", value=0.20, format="%.4f")
        opt_type = st.selectbox("Option Type", ["Call", "Put"])
        
    if st.button("EXECUTE // PRICE OPTION"):
        price, delta, gamma, vega = black_scholes(S, K, T, r, sigma, opt_type.lower())
        
        st.markdown("---")
        st.subheader(">> PRICING OUTPUTS")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("THEORETICAL PRICE", f"${price:.4f}")
        c2.metric("DELTA", f"{delta:.4f}")
        c3.metric("GAMMA", f"{gamma:.4f}")
        c4.metric("VEGA", f"{vega:.4f}")
