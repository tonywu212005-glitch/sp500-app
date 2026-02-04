import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from io import StringIO
import datetime

# Configuration de la page
st.set_page_config(page_title="S&P 500 Calendar", layout="wide")
st.title("📈 Calendrier des Résultats - S&P 500")

@st.cache_data(ttl=24*3600)
def get_sp500_data():
    try:
        # URL de Wikipédia
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        
        # RUSE : On se fait passer pour un navigateur web classique
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # On télécharge la page manuellement
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Vérifie s'il y a une erreur de connexion
        
        # On lit le tableau HTML
        dfs = pd.read_html(StringIO(response.text))
        df = dfs[0]
        
        return df[['Symbol', 'Security', 'GICS Sector']]
        
    except Exception as e:
        st.error(f"Détail de l'erreur technique : {e}")
        return pd.DataFrame()

def get_earnings_date(ticker):
    """Récupère la date via Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        # On essaie plusieurs méthodes car l'API change souvent
        cal = stock.calendar
        if cal is not None and not cal.empty:
            if 'Earnings Date' in cal:
                return cal['Earnings Date'].iloc[0]
            return cal.iloc[0, 0]
    except:
        return None
    return None

# --- AFFICHAGE ---

with st.spinner('Connexion à Wikipédia en cours...'):
    df_sp500 = get_sp500_data()

if df_sp500.empty:
    st.error("Impossible de charger la liste. Wikipédia bloque peut-être la connexion temporairement.")
else:
    st.success(f"✅ Liste chargée : {len(df_sp500)} entreprises trouvées.")
    
    # Sélecteur simple pour tester
    ticker = st.selectbox("Choisis une entreprise pour voir la date :", df_sp500['Symbol'].head(20))
    
    if st.button("Voir la date de résultats"):
        date = get_earnings_date(ticker)
        if date:
            st.metric(label=f"Prochains résultats pour {ticker}", value=str(date))
        else:
            st.warning("Date non confirmée ou introuvable.")

    st.write("Aperçu des données :")
    st.dataframe(df_sp500.head())
