import streamlit as st
import pandas as pd
import urllib.parse

# --- CONFIGURATION ---
st.set_page_config(page_title="CAC 40 Earnings", layout="wide", page_icon="🇫🇷")

st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #004b87;
        color: white;
    }
    .stButton>button:hover {
        background-color: #003366;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("🇫🇷 Calendrier des Résultats - CAC 40")
st.caption("Propulsé par les données de Zonebourse")

# --- 1. DONNÉES STATIQUES ---
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

# --- 2. GÉNÉRATEUR D'URL ZONEBOURSE ---
def generate_zonebourse_url(nom_entreprise):
    """
    Crée une URL de recherche ciblée pour Zonebourse.
    urllib.parse permet de transformer les espaces en %20 pour que le lien soit valide.
    """
    nom_encode = urllib.parse.quote(nom_entreprise)
    # On dirige directement vers le moteur de recherche de Zonebourse
    return f"https://www.zonebourse.com/recherche/?mots={nom_encode}"

# --- 3. INTERFACE ---
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
    if not options:
        st.warning("Aucun résultat.")
        st.stop()
        
    choice = st.radio("Sélection :", options, label_visibility="collapsed")
    nom_entreprise = choice.split(" (")[0]

with col_main:
    st.markdown(f"## 📊 Analyse de **{nom_entreprise}**")
    st.markdown("---")
    
    st.info("💡 En raison des protections anti-robots strictes de Zonebourse, la date ne peut pas être importée automatiquement sur ce serveur.")
    
    # Génération du lien direct
    zb_url = generate_zonebourse_url(nom_entreprise)
    
    # Bouton de redirection Streamlit (ouvre un nouvel onglet)
    st.link_button(f"🔍 Voir l'agenda de {nom_entreprise} sur Zonebourse", zb_url)

st.divider()
with st.expander("Voir la liste complète des tickers CAC 40"):
    st.dataframe(df, use_container_width=True)
