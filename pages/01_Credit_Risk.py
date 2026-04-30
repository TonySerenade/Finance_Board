import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Credit Risk Analysis", layout="wide")

# --- SIDEBAR : Théorie & Formules ---
with st.sidebar:
    st.header("📘 Methodology")
    st.write("""
    The **Altman Z-Score** is a formula for forecasting the probability that a business will enter bankruptcy within two years.
    """)
    st.latex(r"Z = 1.2X_1 + 1.4X_2 + 3.3X_3 + 0.6X_4 + 1.0X_5")
    st.markdown("""
    - **X1**: Working Capital / Total Assets
    - **X2**: Retained Earnings / Total Assets
    - **X3**: EBIT / Total Assets
    - **X4**: Market Cap / Total Liabilities
    - **X5**: Sales / Total Assets
    """)
    st.divider()
    st.header("⚖️ Interpretation")
    st.success("Safe Zone: Z > 2.99")
    st.warning("Grey Zone: 1.81 < Z < 2.99")
    st.error("Distress Zone: Z < 1.81")

# --- MAIN PAGE ---
st.title("🏦 Corporate Credit Risk Scoring")
ticker_input = st.text_input("Search Company Ticker (ex: MSFT, OR.PA, TSLA):", "MSFT")

if ticker_input:
    try:
        company = yf.Ticker(ticker_input)
        info = company.info
        
        # --- Section 1: Company Profile ---
        col_info1, col_info2 = st.columns([1, 2])
        with col_info1:
            if 'logo_url' in info and info['logo_url']:
                st.image(info['logo_url'], width=100)
            st.subheader(info.get('longName', ticker_input))
            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
            st.write(f"**Industry:** {info.get('industry', 'N/A')}")
            st.write(f"**Country:** {info.get('country', 'N/A')}")
        
        with col_info2:
            st.write("**Business Summary:**")
            summary = info.get('longBusinessSummary', 'No summary available.')
            st.write(summary[:500] + "...") # On limite la longueur

        st.divider()

        # --- Section 2: Financial Data Extraction ---
        bs = company.balance_sheet
        is_stmt = company.financials
        
        # Ratios calculations
        ta = bs.loc['Total Assets'].iloc[0]
        re = bs.loc['Retained Earnings'].iloc[0]
        wc = bs.loc['Working Capital'].iloc[0]
        ebit = is_stmt.loc['EBIT'].iloc[0]
        tl = bs.loc['Total Liabilities Net Minority Interest'].iloc[0]
        rev = is_stmt.loc['Total Revenue'].iloc[0]
        mcap = info.get('marketCap', 0)

        x1, x2, x3, x4, x5 = wc/ta, re/ta, ebit/ta, mcap/tl, rev/ta
        z_score = (1.2*x1) + (1.4*x2) + (3.3*x3) + (0.6*x4) + (1.0*x5)

        # --- Section 3: Visualization ---
        st.subheader(f"Final Z-Score: {z_score:.2f}")
        
        if z_score > 2.99:
            st.success(f"**{info.get('shortName')} is in the SAFE ZONE.** This suggests a very low probability of financial distress.")
        elif 1.81 <= z_score <= 2.99:
            st.warning(f"**{info.get('shortName')} is in the GREY ZONE.** Caution is advised, as the company shows signs of financial vulnerability.")
        else:
            st.error(f"**{info.get('shortName')} is in the DISTRESS ZONE.** High probability of bankruptcy within two years according to the model.")

        # --- Section 4: Breakdown Table ---
        with st.expander("See Financial Breakdown"):
            st.table(pd.DataFrame({
                "Metric": ["Working Capital", "Retained Earnings", "EBIT", "Market Cap", "Total Revenue"],
                "Value ($)": [f"{v:,.0f}" for v in [wc, re, ebit, mcap, rev]]
            }))

    except Exception as e:
        st.error("Could not retrieve all financial data. Some tickers (especially banks) might not be compatible with the Altman Z-Score model.")
