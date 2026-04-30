import streamlit as st
import yfinance as yf
import pandas as pd
import requests

st.set_page_config(page_title="Credit Risk Analysis", layout="wide")

# --- FONCTION DE RECHERCHE DYNAMIQUE ---
def get_ticker_suggestions(query):
    if not query or len(query) < 2:
        return {}
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=6&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        return {item['symbol']: f"{item['symbol']} - {item['shortname']}" 
                for item in data.get('quotes', []) if 'shortname' in item}
    except:
        return {}

# --- MAIN PAGE ---
st.title("🏦 Corporate Credit Risk Scoring")

# 1. Recherche Automatique
st.write("### 🔍 Search for a Company")
search_query = st.text_input("Type name or ticker (ex: LVMH, Apple, Airbus):", placeholder="Start typing...")

ticker_to_use = None
if search_query:
    suggestions = get_ticker_suggestions(search_query)
    if suggestions:
        selected_format = st.selectbox("Select the correct entity:", options=list(suggestions.values()))
        ticker_to_use = selected_format.split(" ")[0]
    else:
        ticker_to_use = search_query.upper()

st.divider()

if ticker_to_use:
    try:
        with st.spinner('Fetching financial data...'):
            company = yf.Ticker(ticker_to_use)
            info = company.info
            bs = company.balance_sheet
            is_stmt = company.financials

        # --- Section A: Profil de l'entreprise ---
        col_logo, col_desc = st.columns([1, 4])
        with col_logo:
            if info.get('logo_url'):
                st.image(info['logo_url'], width=120)
        with col_desc:
            st.subheader(info.get('longName', ticker_to_use))
            st.markdown(f"**Sector:** {info.get('sector')} | **Industry:** {info.get('industry')} | **Country:** {info.get('country')}")
            
        st.write("**Business Summary:**")
        st.write(info.get('longBusinessSummary', 'No summary available.')[:600] + "...")

        st.divider()

        # --- Section B: Théorie & Méthodologie (Remise en avant) ---
        st.subheader("📖 Methodology: The Altman Z-Score")
        col_theory, col_scale = st.columns(2)
        
        with col_theory:
            st.write("The formula predicts bankruptcy risk within 2 years using 5 financial ratios:")
            st.latex(r"Z = 1.2X_1 + 1.4X_2 + 3.3X_3 + 0.6X_4 + 1.0X_5")
            st.markdown("""
            - **X1**: Working Capital / Total Assets
            - **X2**: Retained Earnings / Total Assets
            - **X3**: EBIT / Total Assets
            - **X4**: Market Cap / Total Liabilities
            - **X5**: Sales / Total Assets
            """)

        with col_scale:
            st.write("**Risk Scale Interpretation:**")
            st.success("✅ **Safe Zone**: Z > 2.99")
            st.warning("⚠️ **Grey Zone**: 1.81 < Z < 2.99")
            st.error("🚨 **Distress Zone**: Z < 1.81")

        st.divider()

        # --- Section C: Calculs avec gestion d'erreur robuste ---
        # On essaie de récupérer les données avec des noms alternatifs si nécessaire
        try:
            ta = bs.loc['Total Assets'].iloc[0]
            re = bs.loc['Retained Earnings'].iloc[0]
            wc = bs.loc['Working Capital'].iloc[0]
            ebit = is_stmt.loc['EBIT'].iloc[0]
            # Gestion du nom de la dette qui varie souvent
            if 'Total Liabilities Net Minority Interest' in bs.index:
                tl = bs.loc['Total Liabilities Net Minority Interest'].iloc[0]
            else:
                tl = bs.loc['Total Liabilities'].iloc[0]
            
            rev = is_stmt.loc['Total Revenue'].iloc[0]
            mcap = info.get('marketCap', 1)

            x1, x2, x3, x4, x5 = wc/ta, re/ta, ebit/ta, mcap/tl, rev/ta
            z_score = (1.2*x1) + (1.4*x2) + (3.3*x3) + (0.6*x4) + (1.0*x5)

            # --- Section D: Affichage des Résultats ---
            st.subheader(f"Final Score for {ticker_to_use}: {z_score:.2f}")
            
            if z_score > 2.99:
                st.success(f"The company is in the **SAFE ZONE**. Low risk of insolvency.")
            elif 1.81 <= z_score <= 2.99:
                st.warning(f"The company is in the **GREY ZONE**. Financial stability is uncertain.")
            else:
                st.error(f"The company is in the **DISTRESS ZONE**. High risk of bankruptcy.")

            # Tableau des données brutes
            with st.expander("📊 View Raw Financial Data"):
                st.table(pd.DataFrame({
                    "Metric": ["Working Capital", "Retained Earnings", "EBIT", "Market Cap", "Total Revenue"],
                    "Value (USD)": [f"{v:,.0f}" for v in [wc, re, ebit, mcap, rev]]
                }))

        except Exception as calc_error:
            st.error("⚠️ **Financial Extraction Error**: The balance sheet format for this company is non-standard (common for REITs like Mercialys or Banks).")
            st.info("The Altman Z-Score is designed for manufacturing/retail firms, not for Real Estate or Finance sectors.")

    except Exception as e:
        st.error(f"Could not connect to data source for {ticker_to_use}.")

# --- FOOTER ---
st.divider()
st.caption("Data source: Yahoo Finance API | Original Model: Edward Altman (1968)")
