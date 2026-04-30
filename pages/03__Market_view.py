import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Market Intelligence", layout="wide")

# --- FONCTION DE RECHERCHE (AUTOCOMPLETE) ---
def get_ticker_suggestions(query):
    """Récupère les suggestions de tickers via l'API Yahoo Finance."""
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

# --- INTERFACE PRINCIPALE ---
st.title("🗞️ Intelligence & Fundamental Terminal")

# Section de gestion en haut de page (plus ergonomique que la sidebar)
st.markdown("### 📌 Watchlist Management")
col_search, col_list = st.columns([2, 3])

with col_search:
    search_input = st.text_input("🔍 Search & Add Company:", placeholder="Ex: LVMH, Nvidia...")
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
    st.write("**Active Watchlist (Click ❌ to remove):**")
    if st.session_state.watchlist:
        # Création de boutons de suppression horizontaux
        for t in st.session_state.watchlist:
            st.button(f"{t} ❌", key=f"del_{t}", on_click=lambda ticker=t: st.session_state.watchlist.remove(ticker))
    else:
        st.info("Watchlist is empty.")

st.divider()

# --- AFFICHAGE DES RÉSULTATS ---
if st.session_state.watchlist:
    tabs = st.tabs(["🔥 Latest News", "📅 Corporate Agenda", "💎 Fundamentals"])

    # --- TAB 1 : ACTUALITÉS ---
    with tabs[0]:
        for symbol in st.session_state.watchlist:
            with st.expander(f"Recent news for: {symbol}", expanded=True):
                stock = yf.Ticker(symbol)
                news_data = stock.news
                has_content = False
                if news_data:
                    for item in news_data[:3]:
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
                if not has_content:
                    st.warning(f"🔍 **Notice for {symbol}:** Our API is currently unable to find news for this ticker. We're already working on it! :DDD")

    # --- TAB 2 : CALENDRIER (AVEC FALLBACK) ---
    with tabs[1]:
        st.subheader("📅 Corporate Events")
        all_events = []
        for symbol in st.session_state.watchlist:
            try:
                stock = yf.Ticker(symbol)
                cal = stock.calendar
                # Tentative 1 : Calendrier officiel
                if cal is not None and not cal.empty:
                    for index, row in cal.head(3).iterrows():
                        all_events.append({
                            "Ticker": symbol, 
                            "Event": str(index), 
                            "Date": row.iloc[0].strftime('%Y-%m-%d') if hasattr(row.iloc[0], 'strftime') else str(row.iloc[0])
                        })
                # Tentative 2 : Fallback sur les Earnings
                else:
                    earn_date = stock.info.get('earningsTimestampStart')
                    if earn_date:
                        d = datetime.fromtimestamp(earn_date).strftime('%Y-%m-%d')
                        all_events.append({"Ticker": symbol, "Event": "Next Earnings Call", "Date": d})
            except:
                continue
        
        if all_events:
            df_ev = pd.DataFrame(all_events).drop_duplicates().sort_values(by="Date")
            st.dataframe(df_ev, use_container_width=True, hide_index=True)
        else:
            st.warning("🔍 **Notice:** No upcoming events found. We're already working on it! :DDD")

    # --- TAB 3 : FONDAMENTAUX (MODE DASHBOARD) ---
    with tabs[2]:
        for symbol in st.session_state.watchlist:
            try:
                inf = yf.Ticker(symbol).info
                st.markdown(f"### 🏢 {inf.get('shortName', symbol)}")
                c1, c2, c3, c4 = st.columns(4)
                
                c1.metric("Forward P/E", f"{inf.get('forwardPE', 'N/A')}")
                c2.metric("PEG Ratio", f"{inf.get('pegRatio', 'N/A')}")
                
                margin = inf.get('profitMargins', 0)
                c3.metric("Profit Margin", f"{margin*100:.2f}%")
                
                cap = inf.get('marketCap', 0) / 1e9
                c4.metric("Market Cap", f"{cap:.1f}B USD")
                
                st.progress(max(0.0, min(float(margin), 1.0)), text="Profitability Index")
                st.divider()
            except:
                st.error(f"Data error for {symbol}")
else:
    st.warning("👈 Search and add a company above to start.")
