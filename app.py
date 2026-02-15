import streamlit as st
import pandas as pd
import requests
import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="S&P 500 Dashboard", layout="wide", page_icon="🏢")

st.markdown("""
<style>
    /* Style pour les cartes d'entreprises */
    div.stButton > button:first-child {
        background-color: #1e293b !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
        text-align: left !important;
        padding: 15px !important;
        transition: 0.2s !important;
    }
    div.stButton > button:hover {
        background-color: #0f172a !important;
        border-color: #3b82f6 !important;
        transform: translateY(-2px);
    }
    .cap-text {
        color: #10b981; /* Vert émeraude pour l'argent */
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏢 Tableau de Bord S&P 500")
st.markdown("Dates de résultats et Capitalisations boursières en direct via **Finnhub**.")

# --- MÉMOIRE DU SITE ---
if 'ticker_choisi' not in st.session_state:
    st.session_state['ticker_choisi'] = 'AAPL'
if 'nom_choisi' not in st.session_state:
    st.session_state['nom_choisi'] = 'Apple'

# --- 1. SÉCURITÉ ---
st.sidebar.header("⚙️ Configuration API")
api_key = st.sidebar.text_input("🔑 Clé API Finnhub :", type="password")
st.sidebar.markdown("[👉 Créer une clé gratuite ici](https://finnhub.io/)")

# --- 2. FONCTIONS DE RÉCUPÉRATION ---
@st.cache_data(ttl=3600*24)
def get_sp500_list():
    """Récupère la liste officielle des 500 actions."""
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        dfs = pd.read_html(response.text)
        return dfs[0][['Symbol', 'Security', 'GICS Sector']]
    except:
        return pd.DataFrame()

def get_live_company_data(ticker, key):
    """Récupère la capitalisation ET la date de résultats en direct."""
    if not key:
        return None, 0, "Clé API manquante"
        
    clean_ticker = ticker.replace('.', '-')
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=180)
    
    date_resultat = None
    capitalisation = 0
    statut = "✅ En ligne"
    
    # 1. Requête pour la capitalisation (Profile2)
    url_profile = f"https://finnhub.io/api/v1/stock/profile2?symbol={clean_ticker}&token={key}"
    try:
        res_prof = requests.get(url_profile)
        if res_prof.status_code == 429: return None, 0, "Limite API atteinte"
        data_prof = res_prof.json()
        if 'marketCapitalization' in data_prof:
            capitalisation = data_prof['marketCapitalization'] # En millions de dollars
    except:
        pass

    # 2. Requête pour la date de résultats
    url_cal = f"https://finnhub.io/api/v1/calendar/earnings?from={today}&to={end_date}&symbol={clean_ticker}&token={key}"
    try:
        res_cal = requests.get(url_cal)
        data_cal = res_cal.json()
        if "earningsCalendar" in data_cal and len(data_cal["earningsCalendar"]) > 0:
            calendrier = data_cal["earningsCalendar"]
            dates = [datetime.datetime.strptime(item["date"], "%Y-%m-%d").date() for item in calendrier]
            dates.sort()
            date_resultat = dates[0]
    except:
        statut = "Erreur partielle"

    return date_resultat, capitalisation, statut

def format_market_cap(market_cap_millions):
    """Transforme les millions en Milliards (B) ou Trillions (T) pour l'affichage."""
    if market_cap_millions == 0:
        return "N/A"
    elif market_cap_millions > 1000000:
        val = market_cap_millions / 1000000
        return f"$ {val:.2f} T" # Trillions (Milliers de milliards)
    else:
        val = market_cap_millions / 1000
        return f"$ {val:.2f} B" # Billions (Milliards)

# --- 3. INTERFACE PRINCIPALE ---
df_sp500 = get_sp500_list()

if df_sp500.empty:
    st.error("Erreur de connexion à la liste S&P 500.")
    st.stop()

col_liste, col_details = st.columns([1.5, 2])

with col_liste:
    st.subheader("📋 Liste S&P 500 (En direct)")
    
    if not api_key:
        st.warning("⚠️ Entrez votre clé API Finnhub à gauche pour lancer l'analyse en direct.")
    else:
        # --- SYSTÈME DE PAGINATION ---
        ENTREPRISES_PAR_PAGE = 10
        total_pages = (len(df_sp500) // ENTREPRISES_PAR_PAGE) + 1
        
        # Contrôle de la page
        c_prev, c_page, c_next = st.columns([1, 2, 1])
        page_actuelle = c_page.number_input("Aller à la page :", min_value=1, max_value=total_pages, value=1)
        
        start_idx = (page_actuelle - 1) * ENTREPRISES_PAR_PAGE
        end_idx = start_idx + ENTREPRISES_PAR_PAGE
        
        # On extrait uniquement les 10 entreprises de la page actuelle
        df_page = df_sp500.iloc[start_idx:end_idx]
        
        st.caption(f"Affichage des actions {start_idx + 1} à {min(end_idx, len(df_sp500))} sur {len(df_sp500)}")
        
        # Boucle d'affichage pour les 10 entreprises (Lazy Loading)
        with st.spinner("Actualisation des données de la page..."):
            for index, row in df_page.iterrows():
                ticker = row['Symbol']
                nom = row['Security']
                
                # Appel API en direct juste pour cette entreprise
                date_res, cap_millions, status = get_live_company_data(ticker, api_key)
                
                # Formatage de l'affichage
                date_str = date_res.strftime("%d/%m/%Y") if date_res else "Non annoncée"
                cap_str = format_market_cap(cap_millions)
                
                texte_bouton = f"{nom} ({ticker}) | Cap: {cap_str} | 🗓️ {date_str}"
                
                # Bouton cliquable pour mettre à jour la colonne de droite
                if st.button(texte_bouton, key=f"btn_{ticker}", use_container_width=True):
                    st.session_state['ticker_choisi'] = ticker
                    st.session_state['nom_choisi'] = nom

with col_details:
    ticker_actuel = st.session_state['ticker_choisi']
    nom_actuel = st.session_state['nom_choisi']
    
    st.markdown(f"## 🎯 Vue Détaillée : **{nom_actuel}** (`{ticker_actuel}`)")
    st.markdown("---")
    
    if api_key:
        with st.spinner("Chargement des détails..."):
            date_res, cap_millions, status = get_live_company_data(ticker_actuel, api_key)
            
            # Affichage des Metrics en haut
            m1, m2, m3 = st.columns(3)
            
            m1.metric("Capitalisation", format_market_cap(cap_millions))
            
            if date_res:
                m2.metric("Date Résultats", date_res.strftime("%d %b %Y"))
                jours_restants = (date_res - datetime.date.today()).days
                m3.metric("Échéance", f"Dans {jours_restants} jours")
            else:
                m2.metric("Date Résultats", "--")
                m3.metric("Échéance", "--")
                
            st.success(f"Connexion Finnhub : {status}")
            
            # Intégration d'un lien direct vers la page financière Yahoo pour plus d'infos
            clean_ticker_yahoo = ticker_actuel.replace('.', '-')
            st.link_button(f"📈 Voir l'analyse complète de {nom_actuel} sur Yahoo Finance", f"https://finance.yahoo.com/quote/{clean_ticker_yahoo}")
