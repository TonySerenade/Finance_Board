# --- TAB 2 : CALENDAR (LOGIQUE DE REPLI ROBUSTE) ---
    with tabs[1]:
        st.subheader("📅 Corporate Agenda")
        all_events = []
        
        for symbol in st.session_state.watchlist:
            try:
                stock = yf.Ticker(symbol)
                # Tentative 1 : Calendrier officiel
                cal = stock.calendar
                if cal is not None and not cal.empty:
                    for index, row in cal.head(3).iterrows():
                        all_events.append({
                            "Company": symbol, 
                            "Event": str(index), 
                            "Date": row.iloc[0].strftime('%Y-%m-%d') if hasattr(row.iloc[0], 'strftime') else str(row.iloc[0])
                        })
                
                # Tentative 2 : Fallback sur les Earnings & Dividendes via .info
                else:
                    inf = stock.info
                    # Prochains résultats
                    earn_date = inf.get('earningsTimestampStart') or inf.get('nextEarningsDate')
                    if earn_date:
                        d = datetime.fromtimestamp(earn_date).strftime('%Y-%m-%d') if isinstance(earn_date, int) else str(earn_date)
                        all_events.append({"Company": symbol, "Event": "Next Earnings Call", "Date": d})
                    
                    # Prochain dividende
                    div_date = inf.get('dividendDate')
                    if div_date:
                        d = datetime.fromtimestamp(div_date).strftime('%Y-%m-%d') if isinstance(div_date, int) else str(div_date)
                        all_events.append({"Company": symbol, "Event": "Ex-Dividend Date", "Date": d})
            except:
                continue
        
        if all_events:
            # Création du DataFrame et tri chronologique
            df_ev = pd.DataFrame(all_events).drop_duplicates().sort_values(by="Date")
            
            # Affichage stylisé
            st.dataframe(
                df_ev, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Date": st.column_config.DateColumn("Scheduled Date", format="DD/MM/YYYY"),
                    "Event": st.column_config.TextColumn("Description"),
                    "Company": st.column_config.TextColumn("Ticker")
                }
            )
        else:
            # Ton message personnalisé si vraiment rien n'est trouvé
            st.warning("🔍 **Notice:** Our API is currently unable to find upcoming events for these tickers. We're already working on it! :DDD")
