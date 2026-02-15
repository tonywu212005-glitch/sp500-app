import streamlit as st
import pandas as pd
import requests
import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="S&P 500 Earnings", layout="wide", page_icon="🇺🇸")

st.title("🇺🇸 Calendrier des Résultats - S&P 500")
st.markdown("Propulsé par l'API professionnelle **Finnhub** (Données US garanties)")

# --- 1. SÉCURITÉ ET CONFIGURATION DE L'API ---
st.sidebar.header("⚙️ Configuration API")
st.sidebar.markdown("Entrez votre clé API Finnhub pour accéder aux données américaines.")
api_key = st.sidebar.text_input("🔑 Clé API Finnhub :", type="password")
st.sidebar.markdown("[👉 Créer une clé gratuite ici](https://finnhub.io/)")

# --- 2. RÉCUPÉRATION DU S&P 500 ---
@st.cache_data(ttl=3600*24)
def get_sp500_list():
    """Récupère la liste dynamique du S&P 500 via Wikipédia."""
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        dfs = pd.read_html(response.text)
        df = dfs[0]
        return df[['Symbol', 'Security', 'GICS Sector']]
    except Exception as e:
        st.error(f"Erreur de récupération de la liste : {e}")
        return pd.DataFrame()

# --- 3. REQUÊTE API PROFESSIONNELLE ---
def get_earnings_api(ticker, key):
    """Interroge les serveurs de Finnhub pour récupérer la date exacte."""
    if not key:
        return None, "⚠️ Veuillez entrer votre clé API dans le menu à gauche."
        
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=180) # Recherche sur les 6 prochains mois
    
    # Sécurité : Finnhub utilise des tirets au lieu des points pour certains tickers (ex: BRK.B -> BRK-B)
    clean_ticker = ticker.replace('.', '-')
    
    url = f"https://finnhub.io/api/v1/calendar/earnings?from={today}&to={end_date}&symbol={clean_ticker}&token={key}"
    
    try:
        response = requests.get(url)
        
        # Gestion des codes de statut HTTP
        if response.status_code == 401:
            return None, "❌ Clé API invalide."
        elif response.status_code == 429:
            return None, "⏳ Limite de requêtes atteinte."
            
        data = response.json()
        
        # Extraction de la date si elle existe
        if "earningsCalendar" in data and len(data["earningsCalendar"]) > 0:
            calendrier = data["earningsCalendar"]
            dates = [datetime.datetime.strptime(item["date"], "%Y-%m-%d").date() for item in calendrier]
            dates.sort()
            return dates[0], "✅ Donnée certifiée (Finnhub)"
        else:
            return None, "🗓️ Aucune date annoncée pour le moment."
            
    except Exception as e:
        return None, f"Erreur système : {e}"

# --- 4. AFFICHAGE DE L'INTERFACE ---
with st.spinner('Chargement de la base de données S&P 500...'):
    df = get_sp500_list()

if not df.empty:
    col_nav, col_main = st.columns([1, 2])

    with col_nav:
        st.subheader("Sociétés (S&P 500)")
        
        # Moteur de recherche essentiel pour 500 actions
        search = st.text_input("🔍 Rechercher une entreprise", placeholder="Ex: Apple, NVDA, Tesla...")
        
        if search:
            df_display = df[df['Security'].str.contains(search, case=False) | df['Symbol'].str.contains(search, case=False)]
        else:
            st.info("Utilisez la barre de recherche ou choisissez parmi les 30 premières.")
            df_display = df.head(30) # On limite l'affichage par défaut pour ne pas surcharger la page
            
        options = [f"{row['Security']} ({row['Symbol']})" for i, row in df_display.iterrows()]
        
        if not options:
            st.warning("Aucun résultat.")
            st.stop()
            
        choice = st.radio("Sélection :", options, label_visibility="collapsed")
        
        # On extrait proprement le symbole (ex: AAPL)
        code_ticker = choice.split("(")[-1].replace(")", "")
        nom_entreprise = choice.split(" (")[0]

    with col_main:
        st.markdown(f"## 📊 Résultats pour **{nom_entreprise}**")
        st.markdown("---")
        
        if st.button("🔄 Interroger l'API Financière", type="primary", use_container_width=True):
            with st.spinner("Connexion sécurisée aux serveurs Finnhub..."):
                date_res, status = get_earnings_api(code_ticker, api_key)
                
                c1, c2 = st.columns(2)
                
                if date_res:
                    d_str = date_res.strftime("%d/%m/%Y")
                    c1.metric("Date de Publication", d_str)
                    
                    delta = (date_res - datetime.date.today()).days
                    c2.metric("Compte à rebours", f"Dans {delta} jours")
                    st.success(f"Statut : {status}")
                else:
                    c1.metric("Date de Publication", "--")
                    c2.metric("Compte à rebours", "--")
                    st.warning(f"Statut : {status}")

    st.divider()
    with st.expander("Voir la base de données complète (S&P 500)"):
        st.dataframe(df, use_container_width=True)
else:
    st.error("Impossible de charger la liste Wikipédia. Relancez l'application.")
