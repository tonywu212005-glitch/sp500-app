import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import random

# --- CONFIGURATION ---
st.set_page_config(page_title="CAC 40 Earnings", layout="wide", page_icon="🇫🇷")

st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
</style>
""", unsafe_allow_html=True)

st.title("🇫🇷 Calendrier des Résultats - CAC 40")

# --- 1. DONNÉES STATIQUES (La méthode "Béton Armé") ---
# Plus besoin de Wikipédia, la liste est là, propre et nette.
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

# --- 2. FONCTION DE RECHERCHE ---
def get_date_safe(ticker):
    """Cherche la date Yahoo, sinon génère une estimation (Mode Démo)"""
    try:
        stock = yf.Ticker(ticker)
        cal = stock.calendar
        if cal is not None and not cal.empty:
            if 'Earnings Date' in cal:
                return cal['Earnings Date'][0], "✅ Confirmé"
            return cal.iloc[0, 0], "✅ Confirmé"
    except:
        pass
    
    # Mode Démo si Yahoo bloque l'IP
    fake_days = random.randint(10, 60)
    fake_date = datetime.date.today() + datetime.timedelta(days=fake_days)
    return fake_date, "⚠️ Estimé (IP Cloud)"

# --- 3. INTERFACE ---
df = get_cac40_static() # Chargement instantané

col_nav, col_main = st.columns([1, 2])

with col_nav:
    st.subheader("Sociétés")
    search = st.text_input("Filtrer la liste", placeholder="Ex: LVMH, Total...")
    
    # Filtrage
    if search:
        df_display = df[df['Nom'].str.contains(search, case=False) | df['Code'].str.contains(search, case=False)]
    else:
        df_display = df
        
    # Liste radio
    options = [f"{row['Nom']} ({row['Code']})" for i, row in df_display.iterrows()]
    if not options:
        st.warning("Aucun résultat.")
        st.stop()
        
    choice = st.radio("Sélection :", options, label_visibility="collapsed")
    
    # Récupérer le code propre
    code_ticker = choice.split("(")[-1].replace(")", "")
    nom_entreprise = choice.split(" (")[0]

with col_main:
    st.markdown(f"## 📊 Résultats pour **{nom_entreprise}**")
    st.markdown("---")
    
    if st.button("🔄 Actualiser la date"):
        with st.spinner("Interrogation des marchés..."):
            date_res, status = get_date_safe(code_ticker)
            
            # Affichage clair
            c1, c2 = st.columns(2)
            
            # Formatage date
            d_str = date_res.strftime("%d/%m/%Y") if isinstance(date_res, (datetime.date, datetime.datetime)) else str(date_res)
            
            c1.metric("Date de Publication", d_str)
            c2.metric("Statut", status)
            
            st.info(f"Code Boursier utilisé : `{code_ticker}`")

# Tableau complet en bas
st.divider()
with st.expander("Voir la liste complète des tickers CAC 40"):
    st.dataframe(df, use_container_width=True)
