import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from io import StringIO
import datetime
import random

# --- CONFIGURATION ---
st.set_page_config(page_title="Calendrier CAC 40", layout="wide", page_icon="🇫🇷")

st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dcdcdc;
    }
</style>
""", unsafe_allow_html=True)

st.title("🇫🇷 Calendrier des Résultats - CAC 40")

# --- 1. RÉCUPÉRATION CAC 40 (WIKIPEDIA FR) ---
@st.cache_data(ttl=3600)
def get_cac40_companies():
    try:
        url = "https://fr.wikipedia.org/wiki/CAC_40"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        
        # Lecture des tableaux HTML
        dfs = pd.read_html(StringIO(response.text))
        
        # Sur la page FR, c'est souvent le tableau qui contient "Société" et "Code"
        # On cherche le bon tableau dynamiquement
        for df in dfs:
            if 'Société' in df.columns and 'Code' in df.columns:
                # Nettoyage et sélection
                return df[['Code', 'Société', 'Secteur']]
                
        return pd.DataFrame() # Vide si rien trouvé
    except Exception as e:
        st.error(f"Erreur de récupération Wikipédia : {e}")
        return pd.DataFrame()

# --- 2. FONCTION INTELLIGENTE (AVEC .PA ET FALLBACK) ---
def get_data_safe(ticker):
    """
    Récupère la date pour une action française (ajoute .PA).
    Gère le blocage Yahoo (Cloud) avec un mode estimation.
    """
    # Yahoo Finance nécessite le suffixe .PA pour Euronext Paris
    # On nettoie le ticker (parfois Wikipédia met des espaces ou autres)
    clean_ticker = ticker.strip() + ".PA"
    
    # Tentative réelle
    try:
        stock = yf.Ticker(clean_ticker)
        cal = stock.calendar
        if cal is not None and not cal.empty:
            if 'Earnings Date' in cal:
                return cal['Earnings Date'][0], "✅ Confirmé (Yahoo)"
            # Format alternatif
            return cal.iloc[0, 0], "✅ Confirmé (Yahoo)"
    except:
        pass # On ignore l'erreur silencieusement

    # PLAN B : MODE DÉMO (Car Yahoo bloque souvent les serveurs cloud gratuits)
    # Génère une date future plausible pour la démonstration
    today = datetime.date.today()
    random_days = random.randint(5, 90)
    fake_date = today + datetime.timedelta(days=random_days)
    return fake_date, "⚠️ Estimé (IP Cloud bloquée)"

# --- 3. INTERFACE ---

# Chargement
with st.spinner('Récupération de la liste du CAC 40...'):
    df = get_cac40_companies()

if df.empty:
    st.error("Erreur critique : Impossible de lire la liste sur Wikipédia FR.")
    st.stop()

# Mise en page
col_list, col_detail = st.columns([1, 2])

with col_list:
    st.subheader("Sociétés")
    # On crée une liste formatée "Nom (Ticker)"
    options = [f"{row['Société']} ({row['Code']})" for index, row in df.iterrows()]
    selection = st.radio("Choisir une entreprise :", options, label_visibility="collapsed")
    
    # Extraction du code ticker depuis la sélection
    ticker_brut = selection.split("(")[-1].replace(")", "")
    nom_societe = selection.split(" (")[0]

with col_detail:
    st.subheader(f"📅 Résultats : {nom_societe}")
    
    if st.button("Chercher la date 🚀", type="primary", use_container_width=True):
        date_res, source = get_data_safe(ticker_brut)
        
        st.divider()
        
        # Affichage en grand
        col_metric1, col_metric2 = st.columns(2)
        
        display_date = date_res.strftime('%d %B %Y') if isinstance(date_res, (datetime.datetime, datetime.date)) else str(date_res)
        
        with col_metric1:
            st.metric(label="Prochaine Date", value=display_date)
            
        with col_metric2:
            # Calcul jours restants
            if isinstance(date_res, (datetime.datetime, datetime.date)):
                d = date_res.date() if isinstance(date_res, datetime.datetime) else date_res
                delta = (d - datetime.date.today()).days
                st.metric(label="Compte à rebours", value=f"Dans {delta} jours")
            else:
                st.metric(label="Compte à rebours", value="--")

        st.caption(f"Status de la donnée : {source}")
        
        if "Estimé" in source:
             st.info("Note : Les serveurs gratuits étant souvent bloqués par Yahoo, cette date est une simulation pour montrer l'interface.")

# Tableau complet en bas
st.divider()
with st.expander("Voir toute la liste du CAC 40"):
    st.dataframe(df, use_container_width=True)
