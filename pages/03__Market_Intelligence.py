import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Market Intelligence", layout="wide")

# --- FONCTION DE RECHERCHE (AUTOCOMPLETE) ---
def get_ticker_suggestions(query):
    """Récupère les suggestions de tickers depuis Yahoo Finance."""
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

# --- SIDEBAR (GESTION WATCHLIST) ---
with st.sidebar:
    st.header("📌 Market Intelligence")
    st.write("Manage your watchlist here.")
    
    # Barre de recherche par nom
    search_input = st.text_input("🔍 Add Company:", placeholder="Ex: LVMH, Nvidia...")
    
    # Initialisation sécurisée de la watchlist dans la session
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

# --- PAGE PRINCIPALE ---
st.title("🗞️ Intelligence & Fundamental Terminal")

if st.session_state.watchlist:
    # Création des onglets
    tabs = st.tabs(["🔥 Latest News", "📅 Earnings Calendar", "📈 Fundamentals"])

    # --- TAB 1 : ACTUALITÉS ---
    with tabs[0]:
        st.subheader("Market Headlines")
        for symbol in st.session_state.watchlist:
            with st.expander(f"Recent news for: {symbol}", expanded=True):
                stock = yf.Ticker(symbol)
                news_data = stock.news
                
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

                if not has_content:
                    st.warning(f"🔍 **Notice for {symbol}:** Our API is currently unable to fetch news from the source site for this specific ticker. We're already working on it! :DDD")

    # --- TAB 2 : CALENDRIER DES ÉVÉNEMENTS (TOP 5) ---
    with tabs[1]:
        st.subheader("📅 Official Corporate Calendar")
        st.write("Next 5 scheduled corporate events for your watchlist.")
        
        all_events = []
        for symbol in st.session_state.watchlist:
            try:
                stock = yf.Ticker(symbol)
                cal = stock.calendar
                
                if cal is not None and not cal.empty:
                    # On itère sur les 5 premières lignes
                    for index, row in cal.head(5).iterrows():
                        all_events.append({
                            "Ticker": symbol,
                            "Event Type": str(index),
                            "Date": row.iloc[0].strftime('%Y-%m-%d') if hasattr(row.iloc[0], 'strftime') else str(row.iloc[0])
                        })
                else:
                    # Backup sur les prochains résultats si le calendrier complet est vide
                    info = stock.info
                    earn_date = info.get('earningsTimestampStart')
                    if earn_date:
                        date_str = datetime.fromtimestamp(earn_date).strftime('%Y-%m-%d')
                        all_events.append({"Ticker": symbol, "Event Type": "Next Earnings", "Date": date_str})
            except:
                continue

        if all_events:
            df_events = pd.DataFrame(all_events).sort_values(by="Date")
            st.dataframe(
                df_events,
                column_config={
                    "Ticker": st.column_config.TextColumn("Company"),
                    "Event Type": st.column_config.TextColumn("📋 Event Description"),
                    "Date": st.column_config.DateColumn("📅 Date", format="DD/MM/YYYY")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.warning("No official upcoming events found for these tickers.")

    # --- TAB 3 : FONDAMENTAUX ---
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
    st.info("👈 Please add a company in the sidebar to start monitoring.")
