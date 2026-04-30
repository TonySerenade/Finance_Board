import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Credit Risk Scoring", layout="wide")

st.title("🏦 Corporate Credit Risk Scoring")
st.write("This tool calculates the **Altman Z-Score** using real-time financial data.")

ticker = st.text_input("Enter Company Ticker (e.g., AAPL, TSLA, AIR.PA):", "AAPL")

if ticker:
    try:
        data = yf.Ticker(ticker)
        bs = data.balance_sheet
        is_stmt = data.financials
        
        # Extraction des variables
        total_assets = bs.loc['Total Assets'].iloc[0]
        retained_earnings = bs.loc['Retained Earnings'].iloc[0]
        working_capital = bs.loc['Working Capital'].iloc[0]
        ebit = is_stmt.loc['EBIT'].iloc[0]
        total_liabilities = bs.loc['Total Liabilities Net Minority Interest'].iloc[0]
        revenue = is_stmt.loc['Total Revenue'].iloc[0]
        market_cap = data.info.get('marketCap', 0)

        # Calcul des Ratios
        x1 = working_capital / total_assets
        x2 = retained_earnings / total_assets
        x3 = ebit / total_assets
        x4 = market_cap / total_liabilities
        x5 = revenue / total_assets

        z_score = (1.2 * x1) + (1.4 * x2) + (3.3 * x3) + (0.6 * x4) + (1.0 * x5)

        st.subheader(f"Z-Score for {ticker.upper()}: {z_score:.2f}")
        
        if z_score > 2.99:
            st.success("✅ **Safe Zone**: Low probability of bankruptcy.")
        elif 1.81 <= z_score <= 2.99:
            st.warning("⚠️ **Grey Zone**: Significant risk, needs monitoring.")
        else:
            st.error("🚨 **Distress Zone**: High probability of financial distress.")

    except Exception as e:
        st.error(f"Error fetching data. Check ticker or API availability.")
