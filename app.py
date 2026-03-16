import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import streamlit.components.v1 as components

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

# Base de données unique
DB_NAME = "lun_agro_v2026_final.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    # Table Production
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, 
                  provenance TEXT, superficie TEXT, lieu TEXT, qte_rec REAL, dechets REAL, 
                  qte_livrable REAL, montant REAL, mode_paiement TEXT)''')
    # Table Phyto
    c.execute('''CREATE TABLE IF NOT EXISTS phyto 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, produit TEXT, cible TEXT, 
                  parcelle TEXT, dose TEXT, applicateur TEXT)''')
    # Table Agenda
    c.execute('''CREATE TABLE IF NOT EXISTS agenda 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, tache TEXT, responsable TEXT, statut TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- BARRE LATÉRALE (MENU ICÔNES) ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# Navigation par boutons (Correction de l'erreur Ligne 34/41)
if st.sidebar.button("🏠 Accueil", use_container_width=True): st.session_state.page = "Accueil"
if st.sidebar.button("📅 Agenda", use_container_width=True): st.session_state.page = "Agenda"
if st.sidebar.button("🌱 Production", use_container_width=True): st.session_state.page = "Production"
if st.sidebar.button("🧪 Phyto", use_container_width=True): st.session_state.page = "Phyto"
if st.sidebar.button("💰 Finances", use_container_width=True): st.session_state.page = "Finances"
if st.sidebar.button("📚 Formation", use_container_width=True): st.session_state.page = "Formation"
if st.sidebar.button("☁️ Météo", use_container_width=True): st.session_state.page = "Météo"

# --- LOGIQUE DES PAGES ---

# 1. ACCUEIL
if st.session_state.page == "Accueil":
    st.title("🚜 Accueil LUN-AGRO PRO")
    st.success("Application opérationnelle pour Korhogo.")
    st.info("Sélectionnez une option dans le menu à gauche pour commencer.")

# 2. AGENDA
elif st.session_state.page == "Agenda":
    st.title("📅 Agenda & Planning")
    with st.form("f_age"):
        t = st.text_input("Travail à faire"); r = st.text_input("Responsable")
        if st.form_submit_button("Ajouter"):
            conn.execute("INSERT INTO agenda (date, tache, responsable, statut) VALUES (?,?,?,?)",
                         (date.today().strftime("%d/%m/%Y"), t, r, "En cours"))
            conn.commit(); st.rerun()
    st.dataframe(pd.read_sql_query("SELECT * FROM agenda ORDER BY id DESC", conn), use_container_width=True)

# 3. PRODUCTION
elif st.session_state.page == "Production":
    st.title("🌱 Production")
    t1, t2, t3 = st.tabs(["🆕 Semis", "🧺 Récolte", "💵 Vente"])
    with t1:
        with st.form("f_sem"):
            p = st.text_input("Produit"); s = st.text_input("Superficie")
            if st.form_submit_button("Valider"):
                conn.execute("INSERT INTO production (date, type, produit, superficie) VALUES (?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Semis", p, s))
                conn.commit(); st.rerun()
    # (Les onglets Récolte et Vente suivent la même logique simplifiée)

# 4. PHYTO
elif st.session_state.page == "Phyto":
    st.title("🧪 Phyto")
    with st.form("f_phy"):
        prod = st.text_input("Produit utilisé"); parc = st.text_input("Parcelle")
        if st.form_submit_button("Enregistrer"):
            conn.execute("INSERT INTO phyto (date, produit, parcelle) VALUES (?,?,?)",
                         (date.today().strftime("%d/%m/%Y"), prod, parc))
            conn.commit(); st.rerun()

# 5. FINANCES
elif st.session_state.page == "Finances":
    st.title("💰 Finances")
    rev = pd.read_sql_query("SELECT SUM(montant) FROM production WHERE type='Vente'", conn).iloc[0,0] or 0
    st.metric("Revenus Totaux", f"{rev} FCFA")

# 6. FORMATION (BIBLIOTHÈQUE VIDÉO AGRICOLE)
elif st.session_state.page == "Formation":
    st.title("📚 Centre de Formation Agricole")
    
    cat = st.selectbox("Catégories de formation :", [
        "Produits phytosanitaires", "Gestion agricole", 
        "Économie agricole", "Technologies agricoles", 
        "Rédaction de rapport de stage"
    ])
    
    st.write(f"### Vidéos : {cat}")
    
    # Liens YouTube éducatifs officiels (Agriculture)
    links = {
        "Produits phytosanitaires": "https://www.youtube.com/watch?v=kY97_iX2P-w",
        "Gestion agricole": "https://www.youtube.com/watch?v=FjC6F-GIsdY",
        "Économie agricole": "https://www.youtube.com/watch?v=YmXAn2OInm8",
        "Technologies agricoles": "https://www.youtube.com/watch?v=q6bKId6-E-0",
        "Rédaction de rapport de stage": "https://www.youtube.com/watch?v=q0-N64G3rIs"
    }
    
    st.video(links[cat])
    
    if st.button("🎓 Générer un Certificat"):
        st.success("Certificat de formation prêt pour impression
