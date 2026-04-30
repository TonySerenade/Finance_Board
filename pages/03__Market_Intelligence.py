import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Market Intelligence", layout="wide")

# --- FONCTION DE RECHERCHE DYNAMIQUE (Autocomplete) ---
def get_ticker_suggestions(query):
    if not query or len(query) < 2:
        return {}
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=6&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        # Retourne un dictionnaire {Ticker: "Ticker - Nom"}
        return {item['symbol']: f"{item['symbol']} - {item['shortname']}" 
                for item in data.get('quotes', []) if 'shortname' in item}
    except:
        return {}

# --- SIDEBAR : Watchlist Management ---
with st.sidebar:
    st.header("📌 Watchlist Management")
    
    # Barre de recherche par nom (comme sur la page Credit Risk)
    search_input = st.text_input("Search Company Name:", placeholder="Ex: LVMH, Apple...")
    
    # Initialisation de la watchlist dans la session Streamlit pour persistance
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = ["AAPL", "MC.PA"]

    if search_input:
        suggestions = get_ticker_suggestions(search_input)
        if suggestions:
            selected = st.selectbox("Select to add:", options=list(suggestions.values()))
            ticker_to_add = selected.split(" ")[0]
            if st.button(f"Add {ticker_to_add} to Watchlist"):
                if ticker_to_add not in st.session_state.watchlist:
                    st.session_state.watchlist.append(ticker_to_add)
                    st.success(f"{ticker_to_add} added!")

    st.divider()
    st.write("**Current Watchlist:**")
    # Affichage de la liste avec option de suppression
    for t in st.session_state.watchlist:
        col_t, col_del = st.columns([3, 1])
        col_t.write(f"`{t}`")
        if col_del.button("❌", key=f"del_{t}"):
            st.session_state.watchlist.remove(t)
            st.rerun()

# --- MAIN INTERFACE ---
st.title("🗞️ Market Intelligence & News Terminal")

if st.session_state.watchlist:
    tabs = st.tabs(["Latest News", "Corporate Calendar", "Fundamental Metrics"])

    # --- TAB 1 : NEWS FEED (Bug Fix appliqué ici) ---
    with tabs[0]:
        st.subheader("Live Market Headlines")
        for symbol in st.session_state.watchlist:
            with st.expander(f"Recent News for {symbol}"):
                stock = yf.Ticker(symbol)
                news_data = stock.news
                
                if news_data:
                    for item in news_data[:5]:
                        # Correction du bug KeyError : on utilise .get() pour éviter le crash
                        raw_date = item.get('providerPublishTime')
                        if raw_date:
                            pub_date = datetime.fromtimestamp(raw_date).strftime('%Y-%m-%d %H:%M')
                        else:
                            pub_date = "Date unknown"
                            
                        st.markdown(f"**[{item.get('title', 'No Title')}]({item.get('link', '#')})**")
                        st.caption(f"Source: {item.get('publisher', 'Unknown')} | {pub_date}")
                else:
                    st.write("No news available.")

    # --- TAB 2 : CALENDAR ---
    with tabs[1]:
        st.subheader("Upcoming Corporate Events")
        event_list = []
        for symbol in st.session_state.watchlist:
            try:
                info = yf.Ticker(symbol).info
                earn_date = info.get('earningsTimestampStart')
                formatted_date = datetime.fromtimestamp(earn_date).strftime('%Y-%m-%d') if earn_date else "TBD"
                event_list.append({"Ticker": symbol, "Next Earnings": formatted_date})
            except:
                event_list.append({"Ticker": symbol, "Next Earnings": "Data Error"})
        st.table(pd.DataFrame(event_list))

    # --- TAB 3 : FUNDAMENTALS ---
    with tabs[2]:
        st.subheader("Key Valuation Ratios")
        fundamental_data = []
        for symbol in st.session_state.watchlist:
            try:
                inf = yf.Ticker(symbol).info
                fundamental_data.append({
                    "Ticker": symbol,
                    "Market Cap": f"{inf.get('marketCap', 0):,.0f} USD",
                    "Forward P/E": inf.get('forwardPE', 'N/A'),
                    "PEG Ratio": inf.get('pegRatio', 'N/A'),
                    "Profit Margin": f"{inf.get('profitMargins', 0)*100:.2f}%" if inf.get('profitMargins') else "N/A"
                })
            except:
                continue
        st.dataframe(pd.DataFrame(fundamental_data).set_index("Ticker"), use_container_width=True)

else:
    st.info("Your watchlist is empty. Search and add companies in the sidebar.")
