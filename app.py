import streamlit as st
import pandas as pd
import requests
import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="CAC 40 Earnings", layout="wide", page_icon="🇫🇷")

st.title("🇫🇷 Calendrier des Résultats - CAC 40")
st.markdown("Propulsé par l'API professionnelle **Finnhub** (0% de blocage)")

# --- 1. SÉCURITÉ ET CONFIGURATION DE L'API ---
# Méthode pédagogique : L'utilisateur entre sa clé directement sur le site
st.sidebar.header("⚙️ Configuration API")
st.sidebar.markdown("Pour interroger les marchés sans être bloqué, entrez votre clé API Finnhub.")
api_key = st.sidebar.text_input("🔑 Clé API Finnhub :", type="password")
st.sidebar.markdown("[👉 Créer une clé gratuite ici](https://finnhub.io/)")

# --- 2. DONNÉES STATIQUES (CAC 40) ---
@st.cache_data
def get_cac40_static():
    data = [
        {"Code": "AI.PA", "Nom": "Air Liquide", "Secteur": "Matériaux"},
        {"Code": "AIR.PA", "Nom": "Airbus", "Secteur": "Industrie"},
        {"Code": "ALO.PA", "Nom": "Alstom", "Secteur": "Industrie"},
        {"Code": "MT.AS", "Nom": "ArcelorMittal", "Secteur": "Matériaux"},
        {"Code": "CS.PA", "Nom": "AXA", "Secteur": "Finance"},
        {"Code": "BNP.PA", "Nom": "BNP Paribas", "Secteur": "Finance"},
        {"Code": "EN.PA", "Nom": "Bouygues", "Secteur": "Industrie"},
        {"Code": "CAP.PA", "Nom": "Capgemini", "Secteur": "Technologie"},
        {"Code": "CA.PA", "Nom": "Carrefour", "Secteur": "Conso. Base"},
        {"Code": "ACA.PA", "Nom": "Crédit Agricole", "Secteur": "Finance"},
        {"Code": "BN.PA", "Nom": "Danone", "Secteur": "Conso. Base"},
        {"Code": "DSY.PA", "Nom": "Dassault Systèmes", "Secteur": "Technologie"},
        {"Code": "EDEN.PA", "Nom": "Edenred", "Secteur": "Industrie"},
        {"Code": "ENGI.PA", "Nom": "Engie", "Secteur": "Services Publics"},
        {"Code": "EL.PA", "Nom": "EssilorLuxottica", "Secteur": "Santé"},
        {"Code": "RMS.PA", "Nom": "Hermès", "Secteur": "Conso. Discrétionnaire"},
        {"Code": "KER.PA", "Nom": "Kering", "Secteur": "Conso. Discrétionnaire"},
        {"Code": "LR.PA", "Nom": "Legrand", "Secteur": "Industrie"},
        {"Code": "OR.PA", "Nom": "L'Oréal", "Secteur": "Conso. Base"},
        {"Code": "MC.PA", "Nom": "LVMH", "Secteur": "Conso. Discrétionnaire"},
        {"Code": "ML.PA", "Nom": "Michelin", "Secteur": "Conso. Discrétionnaire"},
        {"Code": "ORA.PA", "Nom": "Orange", "Secteur": "Télécoms"},
        {"Code": "RI.PA", "Nom": "Pernod Ricard", "Secteur": "Conso. Base"},
        {"Code": "PUB.PA", "Nom": "Publicis", "Secteur": "Média"},
        {"Code": "RNO.PA", "Nom": "Renault", "Secteur": "Conso. Discrétionnaire"},
        {"Code": "SAF.PA", "Nom": "Safran", "Secteur": "Industrie"},
        {"Code": "SGO.PA", "Nom": "Saint-Gobain", "Secteur": "Industrie"},
        {"Code": "SAN.PA", "Nom": "Sanofi", "Secteur": "Santé"},
        {"Code": "SU.PA", "Nom": "Schneider Electric", "Secteur": "Industrie"},
        {"Code": "GLE.PA", "Nom": "Société Générale", "Secteur": "Finance"},
        {"Code": "STLAP.PA", "Nom": "Stellantis", "Secteur": "Conso. Discrétionnaire"},
        {"Code": "STMPA.PA", "Nom": "STMicroelectronics", "Secteur": "Technologie"},
        {"Code": "TEP.PA", "Nom": "Teleperformance", "Secteur": "Industrie"},
        {"Code": "HO.PA", "Nom": "Thales", "Secteur": "Industrie"},
        {"Code": "TTE.PA", "Nom": "TotalEnergies", "Secteur": "Énergie"},
        {"Code": "URW.AS", "Nom": "Unibail-Rodamco-Westfield", "Secteur": "Immobilier"},
        {"Code": "VIE.PA", "Nom": "Veolia", "Secteur": "Services Publics"},
        {"Code": "DG.PA", "Nom": "Vinci", "Secteur": "Industrie"},
        {"Code": "VIV.PA", "Nom": "Vivendi", "Secteur": "Média"},
    ]
    return pd.DataFrame(data)

# --- 3. REQUÊTE API PROFESSIONNELLE ---
def get_earnings_api(ticker, key):
    """Interroge les serveurs de Finnhub pour récupérer la date exacte."""
    if not key:
        return None, "⚠️ Veuillez entrer votre clé API dans le menu à gauche."
        
    today = datetime.date.today()
    # On recherche les résultats prévus dans les 6 prochains mois
    end_date = today + datetime.timedelta(days=180)
    
    # L'URL exacte de l'API avec nos paramètres
    url = f"https://finnhub.io/api/v1/calendar/earnings?from={today}&to={end_date}&symbol={ticker}&token={key}"
    
    try:
        response = requests.get(url)
        
        # Gestion des erreurs HTTP (comme vu en cours)
        if response.status_code == 401:
            return None, "❌ Clé API invalide ou non reconnue."
        elif response.status_code == 429:
            return None, "⏳ Limite de requêtes atteinte (attendez 1 minute)."
            
        data = response.json()
        
        # Traitement du JSON renvoyé par l'API
        if "earningsCalendar" in data and len(data["earningsCalendar"]) > 0:
            calendrier = data["earningsCalendar"]
            # On convertit les textes en vraies dates et on prend la plus proche
            dates = [datetime.datetime.strptime(item["date"], "%Y-%m-%d").date() for item in calendrier]
            dates.sort()
            return dates[0], "✅ Donnée certifiée (Finnhub)"
        else:
            return None, "🗓️ Aucune date officiellement annoncée pour le moment."
            
    except Exception as e:
        return None, f"Erreur système : {e}"

# --- 4. AFFICHAGE DE L'INTERFACE ---
df = get_cac40_static()

col_nav, col_main = st.columns([1, 2])

with col_nav:
    st.subheader("Sociétés")
    search = st.text_input("Filtrer la liste", placeholder="Ex: LVMH, Total...")
    
    if search:
        df_display = df[df['Nom'].str.contains(search, case=False) | df['Code'].str.contains(search, case=False)]
    else:
        df_display = df
        
    options = [f"{row['Nom']} ({row['Code']})" for i, row in df_display.iterrows()]
    choice = st.radio("Sélection :", options, label_visibility="collapsed")
    
    code_ticker = choice.split("(")[-1].replace(")", "")
    nom_entreprise = choice.split(" (")[0]

with col_main:
    st.markdown(f"## 📊 Résultats pour **{nom_entreprise}**")
    st.markdown("---")
    
    if st.button("🔄 Interroger l'API Financière", type="primary"):
        with st.spinner("Connexion sécurisée aux serveurs Finnhub..."):
            date_res, status = get_earnings_api(code_ticker, api_key)
            
            c1, c2 = st.columns(2)
            
            if date_res:
                d_str = date_res.strftime("%d/%m/%Y")
                c1.metric("Date de Publication", d_str)
                
                # Calcul des jours restants
                delta = (date_res - datetime.date.today()).days
                c2.metric("Compte à rebours", f"Dans {delta} jours")
                st.success(f"Statut : {status}")
            else:
                c1.metric("Date de Publication", "--")
                c2.metric("Compte à rebours", "--")
                st.warning(f"Statut : {status}")

st.divider()
with st.expander("Voir la base de données complète (CAC 40)"):
    st.dataframe(df, use_container_width=True)
