import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from io import StringIO
import datetime

st.set_page_config(page_title="S&P 500 Calendar", layout="wide")
st.title("📈 Calendrier des Résultats - S&P 500")

# --- 1. FONCTION POUR CHARGER LA LISTE (WIKIPEDIA) ---
@st.cache_data(ttl=24*3600)
def get_sp500_data():
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        dfs = pd.read_html(StringIO(response.text))
        return dfs[0][['Symbol', 'Security', 'GICS Sector']]
    except Exception as e:
        st.error(f"Erreur Wikipédia : {e}")
        return pd.DataFrame()

# --- 2. FONCTION POUR TROUVER LA DATE (YAHOO) ---
def get_earnings_date_robust(ticker):
    # CORRECTION CRUCIALE : Remplace le point par un tiret (ex: BRK.B -> BRK-B)
    fmt_ticker = ticker.replace('.', '-')
    
    stock = yf.Ticker(fmt_ticker)
    
    # Méthode 1 : Le calendrier standard
    try:
        cal = stock.calendar
        if cal is not None and not cal.empty:
            # Gestion des différents formats possibles renvoyés par Yahoo
            if isinstance(cal, dict) and 'Earnings Date' in cal:
                return cal['Earnings Date'][0], "Source: Calendrier"
            if isinstance(cal, pd.DataFrame):
                # Parfois la date est en index, parfois en colonne
                if 'Earnings Date' in cal.columns:
                    return cal['Earnings Date'].iloc[0], "Source: Calendrier"
                return cal.iloc[0, 0], "Source: Calendrier (Index)"
    except:
        pass # Si ça rate, on passe à la suite

    # Méthode 2 : Les infos générales (souvent plus fiable)
    try:
        info = stock.info
        # On cherche un timestamp de résultats
        if 'earningsTimestamp' in info:
            ts = info['earningsTimestamp']
            date = datetime.datetime.fromtimestamp(ts)
            return date, "Source: Info Générale"
    except:
        pass

    return None, "Aucune date trouvée"

# --- 3. INTERFACE ---

# Chargement de la liste
with st.spinner('Chargement de la liste S&P 500...'):
    df_sp500 = get_sp500_data()

if not df_sp500.empty:
    # Menu déroulant pour choisir l'action
    col1, col2 = st.columns([1, 2])
    with col1:
        # On met Apple par défaut pour tester car c'est une valeur sûre
        ticker = st.selectbox("Choisir une entreprise", df_sp500['Symbol'].tolist(), index=0)
    
    with col2:
        if st.button("📅 Chercher la date", type="primary"):
            with st.spinner(f"Recherche pour {ticker}..."):
                date, source = get_earnings_date_robust(ticker)
                
                if date:
                    st.success(f"### 🗓️ Prochains résultats : {date}")
                    st.caption(f"({source})")
                else:
                    st.warning("⚠️ Date introuvable via Yahoo Finance.")
                    st.write("Diagnostic : Yahoo peut bloquer les requêtes trop fréquentes depuis le cloud.")

    # Affichage du tableau global (Optionnel)
    with st.expander("Voir la liste complète des entreprises"):
        st.dataframe(df_sp500)
else:
    st.error("La liste est vide. Relancez l'app.")
