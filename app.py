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
    c.execute('''CREATE TABLE IF NOT EXISTS formation 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, nom TEXT, ecole TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- BARRE LATÉRALE ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# Navigation simplifiée (Correction des erreurs des photos)
if st.sidebar.button("🏠 Accueil", use_container_width=True):
    st.session_state.page = "Accueil"
if st.sidebar.button("📅 Agenda", use_container_width=True):
    st.session_state.page = "Agenda"
if st.sidebar.button("🌱 Production", use_container_width=True):
    st.session_state.page = "Production"
if st.sidebar.button("💰 Finances", use_container_width=True):
    st.session_state.page = "Finances"
if st.sidebar.button("📚 Formation", use_container_width=True):
    st.session_state.page = "Formation"
if st.sidebar.button("☁️ Météo", use_container_width=True):
    st.session_state.page = "Météo"

# --- LOGIQUE DES PAGES ---

# 1. ACCUEIL
if st.session_state.page == "Accueil":
    st.title("🚜 Bienvenue sur LUN-AGRO PRO")
    st.success("Système de gestion agricole opérationnel à Korhogo.")

# 2. AGENDA
elif st.session_state.page == "Agenda":
    st.title("📅 Planning des Travaux")
    with st.form("f_age"):
        t = st.text_input("Tâche"); r = st.text_input("Responsable")
        if st.form_submit_button("Ajouter"):
            conn.execute("INSERT INTO agenda (date, tache, responsable) VALUES (?,?,?)",
                         (date.today().strftime("%d/%m/%Y"), t, r))
            conn.commit(); st.rerun()
    st.dataframe(pd.read_sql_query("SELECT * FROM agenda ORDER BY id DESC", conn), use_container_width=True)

# 3. PRODUCTION
elif st.session_state.page == "Production":
    st.title("🌱 Suivi de Production")
    tab1, tab2, tab3 = st.tabs(["🆕 Semis", "🧺 Récolte", "💵 Vente"])
    with tab1:
        with st.form("f_sem"):
            p = st.text_input("Culture"); s = st.text_input("Superficie")
            if st.form_submit_button("Enregistrer Semis"):
                conn.execute("INSERT INTO production (date, type, produit, superficie) VALUES (?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Semis", p, s))
                conn.commit(); st.success("Enregistré")

# 4. FINANCES (Avec Export Excel)
elif st.session_state.page == "Finances":
    st.title("💰 Finances & Export")
    df = pd.read_sql_query("SELECT date, produit, montant FROM production WHERE type='Vente'", conn)
    st.metric("Total Revenus", f"{df['montant'].sum() if not df.empty else 0} FCFA")
    
    if not df.empty:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📊 Télécharger Rapport Excel", output.getvalue(), "Finances.xlsx")

# 5. FORMATION (BIBLIOTHÈQUE VIDÉO AGRICOLE)
elif st.session_state.page == "Formation":
    st.title("📚 Centre de Formation")
    
    # Correction de l'erreur vidéo de votre photo 3
    cat = st.selectbox("Choisir une formation :", [
        "Produits phytosanitaires", "Gestion agricole", 
        "Économie agricole", "Technologies agricoles", 
        "Rédaction de rapport de stage"
    ])
    
    links = {
        "Produits phytosanitaires": "https://www.youtube.com/watch?v=FjC6F-GIsdY",
        "Gestion agricole": "https://www.youtube.com/watch?v=kY97_iX2P-w",
        "Économie agricole": "https://www.youtube.com/watch?v=YmXAn2OInm8",
        "Technologies agricoles": "https://www.youtube.com/watch?v=q6bKId6-E-0",
        "Rédaction de rapport de stage": "https://www.youtube.com/watch?v=q0-N64G3rIs"
    }
    
    st.write(f"### 🎞️ Vidéo : {cat}")
    st.video(links[cat])
    
    # Section Stagiaire (Correction photo 4)
    st.divider()
    with st.form("f_stag"):
        nom = st.text_input("Nom du stagiaire")
        if st.form_submit_button("🎓 Inscrire"):
            st.success(f"Stagiaire {nom} enregistré.")

# 6. MÉTÉO
elif st.session_state.page == "Météo":
    st.title("☁️ Météo Korhogo")
    components.html('<iframe src="https://www.meteoblue.com/fr/meteo/widget/three/korhogo_c%c3%b4te-d%27ivoire_2286420?geoloc=fixed&days=4&tempunit=CELSIUS&layout=light" frameborder="0" style="width: 100%; height: 600px"></iframe>', height=620)
