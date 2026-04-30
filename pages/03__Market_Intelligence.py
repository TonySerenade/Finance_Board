# --- TAB 2 : CALENDAR (TOP 5 EVENTS) ---
    with tabs[1]:
        st.subheader("📅 Official Corporate Calendar")
        st.write("Next 5 scheduled corporate events for your watchlist.")
        
        all_events = []
        for symbol in st.session_state.watchlist:
            try:
                stock = yf.Ticker(symbol)
                # .calendar récupère les événements officiels (Earnings, Ex-Dividend, etc.)
                cal = stock.calendar
                
                if cal is not None and not cal.empty:
                    # On ne garde que les 5 premières lignes du calendrier officiel
                    for index, row in cal.head(5).iterrows():
                        all_events.append({
                            "Ticker": symbol,
                            "Event Type": str(index), # Ex: Earnings, Dividend
                            "Date": row.iloc[0].strftime('%Y-%m-%d') if hasattr(row.iloc[0], 'strftime') else str(row.iloc[0])
                        })
                else:
                    # Si le calendrier spécifique est vide, on tente de récupérer au moins les prochains Earnings
                    info = stock.info
                    earn_date = info.get('earningsTimestampStart')
                    if earn_date:
                        date_str = datetime.fromtimestamp(earn_date).strftime('%Y-%m-%d')
                        all_events.append({"Ticker": symbol, "Event Type": "Next Earnings", "Date": date_str})
            except Exception:
                continue

        if all_events:
            # Création d'un DataFrame pour un affichage propre
            df_events = pd.DataFrame(all_events)
            
            # Tri par date pour avoir les événements les plus proches en haut
            df_events = df_events.sort_values(by="Date")

            # Affichage "Stylisé" via un tableau Streamlit
            st.dataframe(
                df_events,
                column_config={
                    "Ticker": st.column_config.TextColumn("Company", width="small"),
                    "Event Type": st.column_config.TextColumn("📋 Event Description"),
                    "Date": st.column_config.DateColumn("📅 Scheduled Date", format="DD/MM/YYYY")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.warning("No official upcoming events found. Our API might be experiencing delays with the source site, but we're already working on it! :DDD")
