import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import date

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

def crypter(mdp):
    return hashlib.sha256(str.encode(mdp)).hexdigest()

# --- CONNEXION ET CRÉATION SÉCURISÉE ---
DB_PATH = "data_ferme_permanente.db"

def initialiser_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS rh (date TEXT, nom TEXT, poste TEXT, salaire REAL)')
    # Nouvelle structure de table pour correspondre à votre exemple
    c.execute('''CREATE TABLE IF NOT EXISTS depenses 
                 (date TEXT, categorie TEXT, article TEXT, quantite REAL, unite TEXT, prix_unitaire REAL, total REAL)''')
    
    c.execute('SELECT COUNT(*) FROM users WHERE username = "admin"')
    if c.fetchone()[0] == 0:
        admin_pwd = crypter("agri2026")
        c.execute('INSERT INTO users VALUES (?,?,?)', ("admin", admin_pwd, "Administrateur"))
    
    conn.commit()
    return conn

conn = initialiser_db()
c = conn.cursor()

# --- CONNEXION ---
if "connecte" not in st.session_state:
    st.session_state.connecte = False

if not st.session_state.connecte:
    st.title("🔐 Connexion LUN-AGRO")
    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")
    if st.button("SE CONNECTER"):
        c.execute('SELECT password, role FROM users WHERE username = ?', (u,))
        res = c.fetchone()
        if res and res[0] == crypter(p):
            st.session_state.connecte = True
            st.session_state.user_role = res[1]
            st.session_state.username = u
            st.rerun()
    st.stop()

# --- NAVIGATION ---
st.markdown("""<style> div.stButton > button { height: 80px; border-radius: 12px; } </style>""", unsafe_allow_html=True)
if st.session_state.user_role == "Administrateur":
    cols = st.columns(5)
else:
    cols = st.columns(3)

if "page" not in st.session_state: st.session_state.page = "Accueil"

with cols[0]:
    if st.button("🏠\nAccueil"): st.session_state.page = "Accueil"
with cols[1]:
    if st.button("🌱\nProduction"): st.session_state.page = "Production"
with cols[2]:
    if st.button("💰\nFinances"): st.session_state.page = "Finances"

if st.session_state.user_role == "Administrateur":
    with cols[3]:
        if st.button("👥\nRH"): st.session_state.page = "RH"
    with cols[4]:
        if st.button("⚙️\nRéglages"): st.session_state.page = "Réglages"

st.divider()

# --- PAGE FINANCES (VOTRE EXEMPLE PRÉCIS) ---
if st.session_state.page == "Finances":
    st.subheader("💰 Gestion des Dépenses Détaillées")
    
    # Formulaire de saisie détaillé
    with st.expander("➕ Enregistrer un achat (Engrais, Semences, etc.)", expanded=True):
        with st.form("form_achat"):
            c1, c2, c3 = st.columns(3)
            cat = c1.selectbox("Catégorie", ["Intrants", "Matériel", "Transport", "Carburant"])
            art = c2.text_input("Article (ex: UREE, NPK)")
            unite = c3.selectbox("Unité", ["Sac", "Litre", "Kg", "Unité", "Voyage"])
            
            c4, c5 = st.columns(2)
            qte = c4.number_input("Quantité", min_value=0.0, step=1.0)
            prix_u = c5.number_input("Prix Unitaire (FCFA)",
