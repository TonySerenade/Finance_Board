import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Market Intelligence", layout="wide")

# --- FONCTION DE RECHERCHE (AUTOCOMPLETE) ---
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

# --- SIDEBAR (TOUTE LA GESTION EST ICI) ---
with st.sidebar:
    st.header("📌 Market Intelligence")
    st.write("Manage your watchlist and search for entities here.")
    
    # Barre de recherche par nom
    search_input = st.text_input("🔍 Add Company:", placeholder="Ex: LVMH, Nvidia...")
    
    # Initialisation de la watchlist
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = ["AAPL", "MC.PA"]

    if search_input:
        suggestions = get_ticker_suggestions(search_input)
        if suggestions:
            selected = st.selectbox("Confirm Selection:", options=list(suggestions.values()))
            ticker_to_add = selected.split(" ")[0]
            if st.button(f"➕ Add {ticker_to_add}"):
                if ticker_to_add not in st.session_state.watchlist:
                    st.session_state.watchlist.append(ticker_to_add)
                    st.rerun()

    st.divider()
    st.subheader("Your Watchlist")
    
    # Affichage de la liste avec option de suppression
    if st.session_state.watchlist:
        for t in st.session_state.watchlist:
            col_t, col_del = st.columns([4, 1])
            col_t.write(f"**{t}**")
            if col_del.button("❌", key=f"del_{t}"):
                st.session_state.watchlist.remove(t)
                st.rerun()
    else:
        st.write("Watchlist is empty.")

# --- PAGE PRINCIPALE (AFFICHAGE UNIQUEMENT) ---
st.title("🗞️ Intelligence & Fundamental Terminal")

if st.session_state.watchlist:
    tabs = st.tabs(["🔥 Latest News", "📅 Earnings Calendar", "📈 Fundamentals"])


   # --- TAB 1 : NEWS (AVEC MESSAGE PERSONNALISÉ) ---
    with tabs[0]:
        st.subheader("Market Headlines")
        for symbol in st.session_state.watchlist:
            with st.expander(f"Visualizing News for: {symbol}", expanded=True):
                stock = yf.Ticker(symbol)
                news_data = stock.news
                
                # On vérifie s'il y a du contenu ET si les titres ne sont pas vides
                has_content = False
                if news_data:
                    for item in news_data[:5]:
                        title = item.get('title')
                        if title:
                            has_content = True
                            raw_date = item.get('providerPublishTime') or item.get('pubDate')
                            if raw_date and isinstance(raw_date, int):
                                pub_date = datetime.fromtimestamp(raw_date).strftime('%Y-%m-%d %H:%M')
                            else:
                                pub_date = "N/A"
                            
                            st.markdown(f"**[{title}]({item.get('link', '#')})**")
                            st.caption(f"Source: {item.get('publisher', 'Financial Press')} | {pub_date}")
                            st.write("---")

                # --- MESSAGE PERSONNALISÉ SI VIDE ---
                if not has_content:
                    st.warning(f"🔍 **Notice for {symbol}:** Our API is currently unable to fetch news from the source site for this specific ticker. We're already working on it! :DDD")

    
    # --- TAB 2 : CALENDAR ---
    with tabs[1]:
        st.subheader("Corporate Events")
        event_list = []
        for symbol in st.session_state.watchlist:
            try:
                info = yf.Ticker(symbol).info
                earn_date = info.get('earningsTimestampStart')
                formatted_date = datetime.fromtimestamp(earn_date).strftime('%Y-%m-%d') if earn_date else "Check Investor Relations"
                event_list.append({"Ticker": symbol, "Next Earnings": formatted_date})
            except:
                event_list.append({"Ticker": symbol, "Next Earnings": "Unavailable"})
        st.table(pd.DataFrame(event_list))

    # --- TAB 3 : FUNDAMENTALS ---
    with tabs[2]:
        st.subheader("Valuation Snapshot")
        fundamental_data = []
        for symbol in st.session_state.watchlist:
            try:
                inf = yf.Ticker(symbol).info
                fundamental_data.append({
                    "Ticker": symbol,
                    "Name": inf.get('shortName', 'N/A'),
                    "Market Cap": f"{inf.get('marketCap', 0):,.0f}",
                    "Forward P/E": inf.get('forwardPE', 'N/A'),
                    "PEG Ratio": inf.get('pegRatio', 'N/A')
                })
            except:
                continue
        if fundamental_data:
            st.dataframe(pd.DataFrame(fundamental_data).set_index("Ticker"), use_container_width=True)

else:
    st.warning("👈 Start by adding a company in the sidebar to visualize market data.")
