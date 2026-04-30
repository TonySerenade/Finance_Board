import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# Configuration de la page pour un rendu professionnel
st.set_page_config(page_title="Market Intelligence", layout="wide")

st.title("🗞️ Market Intelligence & News Terminal")

# --- SIDEBAR : Gestion de la Watchlist ---
with st.sidebar:
    st.header("📌 Watchlist Management")
    # L'utilisateur peut entrer ses propres tickers
    ticker_list = st.text_input(
        "Enter Tickers (comma separated):", 
        "AAPL, MSFT, TSLA, NVDA, MC.PA",
        help="Use .PA for Paris, .L for London, etc."
    ).upper()
    
    # Nettoyage de la chaîne de caractères pour créer une liste Python
    tickers = [t.strip() for t in ticker_list.split(",")]

# --- MAIN INTERFACE ---
if tickers:
    # Organisation en onglets (Tabs) pour ne pas surcharger l'écran
    tabs = st.tabs(["Latest News", "Corporate Calendar", "Fundamental Metrics"])

    # --- TAB 1 : FLUX D'ACTUALITÉS (News Feed) ---
    with tabs[0]:
        st.subheader("Live Market Headlines")
        for symbol in tickers:
            # Utilisation d'un expander par ticker pour un rendu propre
            with st.expander(f"Recent News for {symbol}"):
                stock = yf.Ticker(symbol)
                news_data = stock.news
                
                if news_data:
                    for item in news_data[:5]: # On limite aux 5 dernières news
                        # Conversion du timestamp UNIX en format lisible (YYYY-MM-DD)
                        pub_date = datetime.fromtimestamp(item['providerPublishTime']).strftime('%Y-%m-%d %H:%M')
                        
                        # Affichage structuré : Titre (lien cliquable) + Source
                        st.markdown(f"**[{item['title']}]({item['link']})**")
                        st.caption(f"Source: {item['publisher']} | {pub_date}")
                else:
                    st.write("No recent news available for this ticker.")

    # --- TAB 2 : CALENDRIER CORPORATE (Earnings/Dividends) ---
    with tabs[1]:
        st.subheader("Upcoming Corporate Events")
        event_list = []
        
        for symbol in tickers:
            stock = yf.Ticker(symbol)
            # Récupération de la date des prochains résultats
            info = stock.info
            earn_date = info.get('earningsTimestampStart')
            
            # Formatage de la date si elle existe
            formatted_date = datetime.fromtimestamp(earn_date).strftime('%Y-%m-%d') if earn_date else "TBD"
            
            event_list.append({
                "Ticker": symbol,
                "Next Earnings Date": formatted_date,
                "Dividend Date": info.get('dividendDate', 'N/A')
            })
        
        # Affichage sous forme de tableau pour comparaison rapide
        if event_list:
            st.table(pd.DataFrame(event_list))

    # --- TAB 3 : FONDAMENTAUX (Fundamental Analysis) ---
    with tabs[2]:
        st.subheader("Key Fundamental Ratios")
        fundamental_data = []
        
        for symbol in tickers:
            inf = yf.Ticker(symbol).info
            # Extraction des metrics clés pour une analyse "Value" ou "Growth"
            fundamental_data.append({
                "Ticker": symbol,
                "Market Cap": f"{inf.get('marketCap', 0):,.0f} USD",
                "Forward P/E": inf.get('forwardPE', 'N/A'),
                "PEG Ratio": inf.get('pegRatio', 'N/A'), # Price/Earnings to Growth
                "Price/Book": inf.get('priceToBook', 'N/A'),
                "Profit Margin": f"{inf.get('profitMargins', 0)*100:.2f}%" if inf.get('profitMargins') else "N/A"
            })
            
        # Affichage d'un DataFrame interactif (triable)
        st.dataframe(pd.DataFrame(fundamental_data).set_index("Ticker"), use_container_width=True)

else:
    st.info("Please enter at least one ticker in the sidebar to start monitoring.")

# --- FOOTER ---
st.divider()
st.caption("Data aggregated from Yahoo Finance. This tool is designed for research and monitoring purposes.")
