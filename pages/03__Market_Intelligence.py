import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURATION PAGE ---
st.set_config(page_title="Market Intelligence", layout="wide")

# --- FONCTION DE RECHERCHE (AUTOCOMPLETE) ---
def get_ticker_suggestions(query):
    """Fetch company suggestions from Yahoo Finance API."""
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

# --- GESTION DE LA SESSION (WATCHLIST) ---
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["AAPL", "MC.PA", "NVDA"]

# --- BARRE DE NAVIGATION / RECHERCHE (TOP OF MAIN PAGE) ---
st.title("🗞️ Intelligence & Fundamental Terminal")

# Zone de recherche moderne en haut
col_search, col_list = st.columns([2, 3])

with col_search:
    search_input = st.text_input("🔍 Search & Add Company:", placeholder="Ex: LVMH, Nvidia, Bitcoin...")
    if search_input:
        suggestions = get_ticker_suggestions(search_input)
        if suggestions:
            selected = st.selectbox("Confirm Selection:", options=list(suggestions.values()))
            ticker_to_add = selected.split(" ")[0]
            if st.button(f"➕ Add {ticker_to_add} to Monitor"):
                if ticker_to_add not in st.session_state.watchlist:
                    st.session_state.watchlist.append(ticker_to_add)
                    st.rerun()

with col_list:
    st.write("**Active Watchlist:**")
    # Affichage horizontal des tickers avec option de suppression
    if st.session_state.watchlist:
        cols = st.columns(len(st.session_state.watchlist))
        for i, t in enumerate(st.session_state.watchlist):
            with cols[i]:
                if st.button(f"{t} ❌", key=f"del_{t}", use_container_width=True):
                    st.session_state.watchlist.remove(t)
                    st.rerun()
    else:
        st.info("Watchlist is empty. Search for a company above.")

st.divider()

# --- AFFICHAGE DES RÉSULTATS ---
if st.session_state.watchlist:
    tabs = st.tabs(["🔥 Latest News", "📅 Earnings Calendar", "💎 Fundamentals"])

    # --- TAB 1 : ACTUALITÉS ---
    with tabs[0]:
        for symbol in st.session_state.watchlist:
            with st.expander(f"Visualizing News for: {symbol}", expanded=True):
                stock = yf.Ticker(symbol)
                news_data = stock.news
                has_content = False
                if news_data:
                    for item in news_data[:3]: # Top 3 pour plus de clarté
                        title = item.get('title')
                        if title:
                            has_content = True
                            raw_date = item.get('providerPublishTime') or item.get('pubDate')
                            pub_date = datetime.fromtimestamp(raw_date).strftime('%Y-%m-%d %H:%M') if isinstance(raw_date, int) else "N/A"
                            st.markdown(f"**[{title}]({item.get('link', '#')})**")
                            st.caption(f"Source: {item.get('publisher', 'Financial Press')} | {pub_date}")
                if not has_content:
                    st.warning(f"🔍 Notice for {symbol}: Our API is unable to fetch news from the source. We're on it! :DDD")

    # --- TAB 2 : CALENDRIER ---
    with tabs[1]:
        st.subheader("Upcoming Events")
        all_events = []
        for symbol in st.session_state.watchlist:
            try:
                stock = yf.Ticker(symbol)
                cal = stock.calendar
                if cal is not None and not cal.empty:
                    for index, row in cal.head(3).iterrows():
                        all_events.append({"Company": symbol, "Event": str(index), "Date": row.iloc[0]})
            except: continue
        
        if all_events:
            df_ev = pd.DataFrame(all_events).sort_values(by="Date")
            st.dataframe(df_ev, use_container_width=True, hide_index=True)
        else:
            st.info("No major events scheduled in the near future.")

    # --- TAB 3 : FUNDAMENTALS (LE GLOW UP) ---
    with tabs[2]:
        st.subheader("Valuation Dashboard")
        
        for symbol in st.session_state.watchlist:
            try:
                inf = yf.Ticker(symbol).info
                st.markdown(f"#### 🏢 {inf.get('shortName', symbol)}")
                
                # Metrics Cards : Bien plus joli qu'un tableau
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Forward P/E", f"{inf.get('forwardPE', 'N/A')}")
                m2.metric("PEG Ratio", f"{inf.get('pegRatio', 'N/A')}")
                m3.metric("Profit Margin", f"{inf.get('profitMargins', 0)*100:.2f}%")
                m4.metric("Market Cap", f"{inf.get('marketCap', 0)/1e9:.1f}B")
                
                # Barre de progression visuelle pour la marge (exemple de design)
                margin = inf.get('profitMargins', 0)
                st.progress(max(0, min(float(margin), 1.0)), text=f"Profitability Index ({margin*100:.1f}%)")
                st.divider()
            except:
                st.error(f"Could not load data for {symbol}")

else:
    st.warning("Search and add a company above to unlock the terminal.")
