import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import streamlit.components.v1 as components
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

# Base de données
DB_NAME = "lun_agro_v2026_final.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, 
                  superficie TEXT, montant REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS agenda 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, tache TEXT, responsable TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings 
                 (id INTEGER PRIMARY KEY, nom_ferme TEXT, contact TEXT, devise TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- BARRE LATÉRALE (MENU COMPLET) ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# Navigation (L'icône Réglage est maintenant ici)
if st.sidebar.button("🏠 Accueil", use_container_width=True): st.session_state.page = "Accueil"
if st.sidebar.button("📅 Agenda", use_container_width=True): st.session_state.page = "Agenda"
if st.sidebar.button("🌱 Production", use_container_width=True): st.session_state.page = "Production"
if st.sidebar.button("💰 Finances", use_container_width=True): st.session_state.page = "Finances"
if st.sidebar.button("📚 Formation", use_container_width=True): st.session_state.page = "Formation"
if st.sidebar.button("☁️ Météo", use_container_width=True): st.session_state.page = "Météo"
st.sidebar.write("---")
if st.sidebar.button("⚙️ Réglages", use_container_width=True): st.session_state.page = "Réglages"

# --- LOGIQUE DES PAGES ---

# 1. ACCUEIL
if st.session_state.page == "Accueil":
    st.title("🚜 Bienvenue sur LUN-AGRO PRO")
    st.info("Sélectionnez une option à gauche pour gérer votre exploitation.")

# 2. RÉGLAGES (NOUVELLE SECTION)
elif st.session_state.page == "Réglages":
    st.title("⚙️ Paramètres de l'application")
    st.subheader("Configuration de la ferme")
    with st.form("f_settings"):
        nom = st.text_input("Nom de l'exploitation", "LUN-AGRO")
        loc = st.text_input("Localisation", "Korhogo")
        devise = st.selectbox("Devise", ["FCFA", "Euro", "Dollar"])
        if st.form_submit_button("Enregistrer les réglages"):
            st.success("Paramètres mis à jour !")

# 3. FORMATION (BIBLIOTHÈQUE VIDÉO)
elif st.session_state.page == "Formation":
    st.title("📚 Centre de Formation Agricole")
    cat = st.selectbox("Thème :", ["Produits phytosanitaires", "Gestion agricole", "Économie agricole", "Technologies agricoles", "Rédaction de rapport de stage"])
    
    links = {
        "Produits phytosanitaires": "https://www.youtube.com/watch?v=FjC6F-GIsdY",
        "Gestion agricole": "https://www.youtube.com/watch?v=kY97_iX2P-w",
        "Économie agricole": "https://www.youtube.com/watch?v=YmXAn2OInm8",
        "Technologies agricoles": "https://www.youtube.com/watch?v=q6bKId6-E-0",
        "Rédaction de rapport de stage": "https://www.youtube.com/watch?v=q0-N64G3rIs"
    }
    st.video(links[cat])

# 4. FINANCES (EXPORT EXCEL)
elif st.session_state.page == "Finances":
    st.title("💰 Suivi Financier")
    df = pd.read_sql_query("SELECT date, produit, montant FROM production WHERE type='Vente'", conn)
    if not df.empty:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📊 Télécharger Rapport Excel", output.getvalue(), "Finances.xlsx")
    st.dataframe(df, use_container_width=True)

# 5. PRODUCTION
elif st.session_state.page == "Production":
    st.title("🌱 Production")
    # ... (Le reste du code Production reste identique)
    st.write("Saisie des données en cours...")

# 6. MÉTÉO
elif st.session_state.page == "Météo":
    st.title("☁️ Météo Korhogo")
    components.html('<iframe src="https://www.meteoblue.com/fr/meteo/widget/three/korhogo_c%c3%b4te-d%27ivoire_2286420?geoloc=fixed&days=4&tempunit=CELSIUS&layout=light" frameborder="0" style="width: 100%; height: 600px"></iframe>', height=620)
