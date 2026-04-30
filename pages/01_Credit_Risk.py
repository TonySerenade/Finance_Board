import streamlit as st
import yfinance as yf
import pandas as pd
import requests

st.set_page_config(page_title="Credit Risk Analysis", layout="wide")

# --- FONCTION DE RECHERCHE AUTOMATIQUE ---
def get_ticker_suggestions(query):
    if not query or len(query) < 2:
        return {}
    try:
        # On interroge l'API de suggestion de Yahoo
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=6&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # On extrait les tickers et les noms
        suggestions = {item['symbol']: f"{item['symbol']} - {item['shortname']}" 
                       for item in data.get('quotes', []) 
                       if 'shortname' in item}
        return suggestions
    except:
        return {}

# --- MAIN PAGE ---
st.title("🏦 Corporate Credit Risk Scoring")

# 1. Barre de recherche dynamique
st.write("### Search for a Company")
search_query = st.text_input("Type company name or ticker (ex: LVMH, Apple, Airbus):", "")

ticker_to_use = None

if search_query:
    suggestions = get_ticker_suggestions(search_query)
    
    if suggestions:
        # On affiche les résultats trouvés sous forme de menu
        selected_format = st.selectbox(
            "Select the correct entity:",
            options=list(suggestions.values()),
            index=0
        )
        # On récupère juste le ticker (la partie avant le premier espace)
        ticker_to_use = selected_format.split(" ")[0]
    else:
        # Si aucune suggestion mais que l'utilisateur a tapé un truc qui ressemble à un ticker
        ticker_to_use = search_query.upper()

st.divider()

# --- RESTE DU CODE (LOGIQUE FINANCIÈRE) ---
if ticker_to_use:
    try:
        company = yf.Ticker(ticker_to_use)
        info = company.info
        
        if 'longName' not in info:
            st.warning("⚠️ Data incomplete for this ticker. Trying to fetch financial statements anyway...")
        
        # Affichage du profil
        col_info1, col_info2 = st.columns([1, 3])
        with col_info1:
            if info.get('logo_url'):
                st.image(info['logo_url'], width=120)
            st.subheader(info.get('longName', ticker_to_use))
        
        with col_info2:
            st.markdown(f"**Sector:** {info.get('sector')} | **Country:** {info.get('country')}")
            st.write(info.get('longBusinessSummary', 'No summary available.')[:500] + "...")

        # Extraction et Calcul (Z-Score)
        bs = company.balance_sheet
        is_stmt = company.financials
        
        # On récupère les valeurs
        ta = bs.loc['Total Assets'].iloc[0]
        re = bs.loc['Retained Earnings'].iloc[0]
        wc = bs.loc['Working Capital'].iloc[0]
        ebit = is_stmt.loc['EBIT'].iloc[0]
        tl = bs.loc['Total Liabilities Net Minority Interest'].iloc[0]
        rev = is_stmt.loc['Total Revenue'].iloc[0]
        mcap = info.get('marketCap', 1)

        x1, x2, x3, x4, x5 = wc/ta, re/ta, ebit/ta, mcap/tl, rev/ta
        z_score = (1.2*x1) + (1.4*x2) + (3.3*x3) + (0.6*x4) + (1.0*x5)

        st.subheader(f"Z-Score Result: {z_score:.2f}")
        
        if z_score > 2.99: st.success("✅ SAFE ZONE")
        elif 1.81 <= z_score <= 2.99: st.warning("⚠️ GREY ZONE")
        else: st.error("🚨 DISTRESS ZONE")

    except Exception as e:
        st.error("Financial data unavailable for this specific ticker (typical for banks or recent IPOs).")
