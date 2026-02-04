import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Calendrier Earnings S&P 500",
    page_icon="📈",
    layout="wide"
)

# --- CSS PERSONNALISÉ (Pour faire joli) ---
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS (BACKEND) ---

@st.cache_data(ttl=24*3600)  # Cache les données pour 24h
def get_sp500_list():
    """Récupère la liste à jour du S&P 500 depuis Wikipedia."""
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        df = tables[0]
        return df[['Symbol', 'Security', 'GICS Sector']]
    except Exception as e:
        st.error("Erreur lors de la récupération de la liste S&P 500.")
        return pd.DataFrame()

def get_next_earnings_date(ticker):
    """Récupère la prochaine date de résultats pour un ticker donné."""
    try:
        stock = yf.Ticker(ticker)
        
        # Yahoo Finance renvoie parfois un dataframe, parfois un dict, parfois rien.
        # On essaie de récupérer le calendrier
        cal = stock.calendar
        
        if cal is None:
            return None
            
        # Gestion des différents formats de retour de l'API yfinance
        if isinstance(cal, dict):
            if 'Earnings Date' in cal:
                dates = cal['Earnings Date']
                if len(dates) > 0:
                    return dates[0]
            elif 0 in cal: # Parfois la clé est l'index 0
                return cal[0]
                
        elif isinstance(cal, pd.DataFrame):
            if not cal.empty:
                # Si c'est un DataFrame, la date est souvent dans la première colonne ou ligne
                return cal.iloc[0, 0]
                
        return None
    except Exception:
        return None

# --- INTERFACE UTILISATEUR (FRONTEND) ---

st.title("📅 Calendrier des Résultats S&P 500")
st.markdown("Suivez les dates de publication des résultats financiers des entreprises américaines.")

# 1. Chargement de la liste
with st.spinner('Récupération de la liste des entreprises...'):
    df_sp500 = get_sp500_list()

if df_sp500.empty:
    st.stop()

# 2. Barre latérale (Contrôles)
st.sidebar.header("🔍 Filtres de recherche")

# Option pour limiter la recherche (CRUCIAL pour la performance)
search_mode = st.sidebar.radio(
    "Mode de recherche :",
    ("Par Secteur (Recommandé)", "Ticker spécifique", "Top 20 (Démo)")
)

selected_tickers = []

if search_mode == "Par Secteur (Recommandé)":
    sectors = sorted(df_sp500['GICS Sector'].unique())
    selected_sector = st.sidebar.selectbox("Choisissez un secteur :", sectors)
    # On filtre le dataframe
    df_filtered = df_sp500[df_sp500['GICS Sector'] == selected_sector]
    st.info(f"Secteur **{selected_sector}** : {len(df_filtered)} entreprises trouvées.")
    
    if st.sidebar.button("Lancer la recherche pour ce secteur"):
        selected_tickers = df_filtered.to_dict('records')

elif search_mode == "Ticker spécifique":
    ticker_input = st.sidebar.text_input("Entrez le symbole (ex: NVDA, AAPL)", "").upper()
    if ticker_input:
        row = df_sp500[df_sp500['Symbol'] == ticker_input]
        if not row.empty:
            selected_tickers = row.to_dict('records')
        else:
            st.sidebar.warning("Ce ticker n'est pas dans le S&P 500.")

elif search_mode == "Top 20 (Démo)":
    st.sidebar.info("Affiche les 20 premières entreprises de la liste.")
    selected_tickers = df_sp500.head(20).to_dict('records')

# 3. Récupération et Affichage des Résultats
if selected_tickers:
    results_data = []
    
    # Barre de progression
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = len(selected_tickers)
    
    for i, row in enumerate(selected_tickers):
        # Mise à jour progression
        status_text.text(f"Analyse de {row['Security']} ({i+1}/{total})...")
        progress_bar.progress((i + 1) / total)
        
        # Appel API
        date = get_next_earnings_date(row['Symbol'])
        
        # Formatage de la date pour l'affichage
        date_str = "Non confirmé"
        days_left = ""
        
        if date:
            # Si c'est un objet date/datetime, on formate
            if isinstance(date, (datetime, pd.Timestamp)):
                date_str = date.strftime('%d/%m/%Y')
                
                # Calcul du nombre de jours restants
                delta = date.date() - datetime.now().date() if isinstance(date, datetime) else date.date() - datetime.now().date()
                if delta.days == 0:
                    days_left = "🚨 AUJOURD'HUI"
                elif delta.days > 0:
                    days_left = f"dans {delta.days} jours"
                else:
                    days_left = "Passé"

        results_data.append({
            "Symbole": row['Symbol'],
            "Entreprise": row['Security'],
            "Secteur": row['GICS Sector'],
            "Date Résultats": date_str,
            "Statut": days_left
        })
    
    status_text.empty()
    progress_bar.empty()
    
    # Création du DataFrame final
    df_results = pd.DataFrame(results_data)
    
    # Affichage du tableau interactif
    st.success("Chargement terminé !")
    
    st.dataframe(
        df_results,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Symbole": st.column_config.TextColumn("Symbole", help="Ticker boursier"),
            "Date Résultats": st.column_config.TextColumn("Date Prévue"),
            "Statut": st.column_config.TextColumn("Compte à rebours"),
        }
    )
    
    # Bouton de téléchargement CSV
    csv = df_results.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger ce tableau en CSV",
        data=csv,
        file_name='resultats_sp500.csv',
        mime='text/csv',
    )

else:
    if search_mode == "Par Secteur (Recommandé)":
        st.write("👈 Cliquez sur le bouton **'Lancer la recherche'** dans la barre latérale.")
    elif search_mode == "Ticker spécifique":
        st.write("👈 Entrez un ticker dans la barre latérale.")
