import streamlit as st
import pandas as pd
import requests
import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="S&P 500 Earnings", layout="wide", page_icon="🏆")

# Design personnalisé pour les boutons du classement
st.markdown("""
<style>
    .stButton>button {
        text-align: left;
        width: 100%;
        border-radius: 8px;
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        transition: 0.3s;
    }
    .stButton>button:hover {
        border-color: #004b87;
        background-color: #eef2f5;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏆 Calendrier des Résultats - S&P 500")
st.markdown("Propulsé par l'API professionnelle **Finnhub**")

# --- MÉMOIRE DU SITE (SESSION STATE) ---
# C'est ici qu'on demande à Streamlit de se souvenir du choix de l'utilisateur
if 'ticker_choisi' not in st.session_state:
    st.session_state['ticker_choisi'] = 'NVDA' # Nvidia par défaut
if 'nom_choisi' not in st.session_state:
    st.session_state['nom_choisi'] = 'Nvidia'

# --- 1. SÉCURITÉ ET API ---
st.sidebar.header("⚙️ Configuration API")
api_key = st.sidebar.text_input("🔑 Clé API Finnhub :", type="password")
st.sidebar.markdown("[👉 Créer une clé gratuite ici](https://finnhub.io/)")

# --- 2. FONCTIONS DE RÉCUPÉRATION ---
@st.cache_data(ttl=3600*24)
def get_sp500_list():
    """Récupère la liste complète des 500 entreprises."""
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        dfs = pd.read_html(response.text)
        return dfs[0][['Symbol', 'Security', 'GICS Sector']]
    except:
        return pd.DataFrame()

def get_earnings_api(ticker, key):
    """Interroge Finnhub pour une entreprise spécifique."""
    if not key:
        return None, "Clé API manquante"
        
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=180)
    clean_ticker = ticker.replace('.', '-')
    url = f"https://finnhub.io/api/v1/calendar/earnings?from={today}&to={end_date}&symbol={clean_ticker}&token={key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 401: return None, "Clé API invalide"
        if response.status_code == 429: return None, "Limite atteinte (60/min)"
            
        data = response.json()
        if "earningsCalendar" in data and len(data["earningsCalendar"]) > 0:
            calendrier = data["earningsCalendar"]
            dates = [datetime.datetime.strptime(item["date"], "%Y-%m-%d").date() for item in calendrier]
            dates.sort()
            return dates[0], "✅ Donnée certifiée"
        return None, "Aucune date annoncée"
    except:
        return None, "Erreur serveur"

@st.cache_data(ttl=3600*12) # On met en cache pour économiser nos 60 requêtes/minute !
def load_top_ranking(key):
    """Charge les dates pour le Top 15 des capitalisations boursières mondiales."""
    top_15 = [
        ("NVDA", "Nvidia"), ("AAPL", "Apple"), ("MSFT", "Microsoft"),
        ("AMZN", "Amazon"), ("GOOGL", "Alphabet (Google)"), ("META", "Meta"),
        ("BRK.B", "Berkshire Hathaway"), ("LLY", "Eli Lilly"), ("AVGO", "Broadcom"),
        ("TSLA", "Tesla"), ("JPM", "JPMorgan Chase"), ("V", "Visa"),
        ("UNH", "UnitedHealth"), ("XOM", "ExxonMobil"), ("MA", "Mastercard")
    ]
    resultats = []
    for ticker, nom in top_15:
        date_res, _ = get_earnings_api(ticker, key)
        resultats.append({"Ticker": ticker, "Nom": nom, "Date": date_res})
    return resultats

# --- 3. AFFICHAGE DE L'INTERFACE ---
df_sp500 = get_sp500_list()

# Mise en page : Colonne de gauche (Classement & Recherche) / Droite (Résultats)
col_nav, col_main = st.columns([1.2, 2])

with col_nav:
    # 3.A MOTEUR DE RECHERCHE
    st.subheader("🔍 Recherche Spécifique")
    search = st.text_input("Chercher parmi les 500 actions :", placeholder="Ex: Netflix, AMD...")
    
    if search and not df_sp500.empty:
        df_search = df_sp500[df_sp500['Security'].str.contains(search, case=False) | df_sp500['Symbol'].str.contains(search, case=False)]
        if not df_search.empty:
            for i, row in df_search.head(5).iterrows():
                # Bouton de recherche : s'il est cliqué, on met à jour la mémoire du site
                if st.button(f"🔎 {row['Security']} ({row['Symbol']})", key=f"search_{row['Symbol']}"):
                    st.session_state['ticker_choisi'] = row['Symbol']
                    st.session_state['nom_choisi'] = row['Security']
    
    st.divider()
    
    # 3.B CLASSEMENT TOP 15 (Le cœur de ta demande)
    st.subheader("👑 Top 15 Capitalisations")
    if not api_key:
        st.info("⚠️ Entrez votre clé API à gauche pour charger le classement.")
    else:
        with st.spinner("Analyse du Top 15..."):
            top_data = load_top_ranking(api_key)
            
            for index, item in enumerate(top_data):
                # Formatage de la date pour le bouton
                if item["Date"]:
                    date_affichee = item["Date"].strftime("%d/%m/%Y")
                else:
                    date_affichee = "À venir"
                
                # Création du texte du bouton (ex: "1. Apple (AAPL) - 🗓️ 25/04/2026")
                texte_bouton = f"**{index + 1}. {item['Nom']}** ({item['Ticker']}) ➔ 🗓️ {date_affichee}"
                
                # Bouton cliquable : s'il est cliqué, on met à jour la mémoire !
                if st.button(texte_bouton, key=f"btn_{item['Ticker']}", use_container_width=True):
                    st.session_state['ticker_choisi'] = item['Ticker']
                    st.session_state['nom_choisi'] = item['Nom']

with col_main:
    # On affiche toujours les données de l'entreprise mémorisée dans la session
    ticker_actuel = st.session_state['ticker_choisi']
    nom_actuel = st.session_state['nom_choisi']
    
    st.markdown(f"## 📊 Focus sur **{nom_actuel}** (`{ticker_actuel}`)")
    st.markdown("---")
    
    if api_key:
        with st.spinner("Récupération en direct..."):
            date_res, status = get_earnings_api(ticker_actuel, api_key)
            
            # Affichage de style "Dashboard"
            c1, c2 = st.columns(2)
            
            if date_res:
                c1.metric("🗓️ Date de Publication", date_res.strftime("%d %B %Y"))
                
                jours_restants = (date_res - datetime.date.today()).days
                if jours_restants == 0:
                    c2.metric("⏳ Compte à rebours", "🚨 C'est aujourd'hui !")
                elif jours_restants < 0:
                    c2.metric("⏳ Compte à rebours", "Passé")
                else:
                    c2.metric("⏳ Compte à rebours", f"Dans {jours_restants} jours")
                    
                st.success(f"Statut du serveur : {status}")
            else:
                c1.metric("🗓️ Date de Publication", "--")
                c2.metric("⏳ Compte à rebours", "--")
                st.warning(f"Statut : {status}")
    else:
        st.warning("👈 Veuillez entrer votre clé API dans le menu de gauche pour voir les détails.")
