import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="SP500 Résultats", layout="wide")

st.title("📅 Calendrier SP500")

@st.cache_data
def load_data():
    try:
        # Liste simplifiée pour le test
        sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        return sp500[['Symbol', 'Security', 'GICS Sector']].head(20) # On prend les 20 premiers pour le test
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.write("Voici les 20 premières entreprises (Test de fonctionnement) :")
    st.dataframe(df)
else:
    st.error("Erreur de chargement des données.")
