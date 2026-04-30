import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Credit Risk Analysis", layout="wide")

# --- MAIN PAGE ---
st.title("🏦 Corporate Credit Risk Scoring")

# 1. Input Section
ticker_input = st.text_input("Search Company Ticker (ex: MSFT, OR.PA, TSLA):", "MSFT")

if ticker_input:
    try:
        company = yf.Ticker(ticker_input)
        info = company.info
        
        # --- Section 1: Company Profile ---
        col_info1, col_info2 = st.columns([1, 3])
        with col_info1:
            if 'logo_url' in info and info['logo_url']:
                st.image(info['logo_url'], width=120)
            st.subheader(info.get('longName', ticker_input))
        
        with col_info2:
            st.markdown(f"""
            **Sector:** {info.get('sector', 'N/A')} | **Industry:** {info.get('industry', 'N/A')} | **Country:** {info.get('country', 'N/A')}
            
            **Business Summary:**
            {info.get('longBusinessSummary', 'No summary available.')[:600]}...
            """)

        st.divider()

        # --- Section 2: Theory & Methodology (Moved to Main) ---
        with st.expander("📖 View Model Methodology & Formulas"):
            st.write("""
            The **Altman Z-Score** is a multivariate statistical formula used to predict the probability that a firm will go bankrupt within two years. 
            It was published by Edward I. Altman in 1968.
            """)
            st.latex(r"Z = 1.2X_1 + 1.4X_2 + 3.3X_3 + 0.6X_4 + 1.0X_5")
            st.markdown("""
            - **X1 (Liquidity)**: Working Capital / Total Assets
            - **X2 (Solvency)**: Retained Earnings / Total Assets
            - **X3 (Profitability)**: EBIT / Total Assets
            - **X4 (Leverage)**: Market Value of Equity / Total Liabilities
            - **X5 (Efficiency)**: Sales / Total Assets
            """)
            st.info("**Interpretation:** Safe (Z > 2.99) | Grey (1.81 - 2.99) | Distress (Z < 1.81)")

        # --- Section 3: Financial Data Extraction ---
        bs = company.balance_sheet
        is_stmt = company.financials
        
        # Extraction des métriques
        ta = bs.loc['Total Assets'].iloc[0]
        re = bs.loc['Retained Earnings'].iloc[0]
        wc = bs.loc['Working Capital'].iloc[0]
        ebit = is_stmt.loc['EBIT'].iloc[0]
        tl = bs.loc['Total Liabilities Net Minority Interest'].iloc[0]
        rev = is_stmt.loc['Total Revenue'].iloc[0]
        mcap = info.get('marketCap', 1) # Éviter division par zéro

        # Calcul des Ratios
        x1, x2, x3, x4, x5 = wc/ta, re/ta, ebit/ta, mcap/tl, rev/ta
        z_score = (1.2*x1) + (1.4*x2) + (3.3*x3) + (0.6*x4) + (1.0*x5)

        # --- Section 4: Result Display ---
        st.subheader(f"Analysis Result: {z_score:.2f}")
        
        if z_score > 2.99:
            st.success(f"✅ **SAFE ZONE**: {info.get('shortName')} shows a very low probability of bankruptcy.")
        elif 1.81 <= z_score <= 2.99:
            st.warning(f"⚠️ **GREY ZONE**: Financial vulnerability detected. The company should be monitored.")
        else:
            st.error(f"🚨 **DISTRESS ZONE**: High risk of financial distress within the next 24 months.")

        # --- Section 5: Data Transparency ---
        col_tab1, col_tab2 = st.columns(2)
        with col_tab1:
            st.write("**Financial Metrics Used (USD):**")
            st.table(pd.DataFrame({
                "Metric": ["Working Capital", "Retained Earnings", "EBIT", "Market Cap", "Total Revenue"],
                "Value": [f"{v:,.0f}" for v in [wc, re, ebit, mcap, rev]]
            }))
        
        with col_tab2:
            st.write("**Model Sources:**")
            st.markdown("""
            - **Financial Data:** Real-time extraction via [Yahoo Finance API](https://finance.yahoo.com/).
            - **Original Study:** Altman, E. I. (1968). *Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy*. Journal of Finance.
            - **Note:** This model is intended for manufacturing/public firms. It may not be suitable for financial institutions or insurance companies.
            """)

    except Exception as e:
        st.error(f"Error: Could not retrieve sufficient data for {ticker_input}. This often happens with banks or companies with irregular financial reporting.")
