import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import date

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

def crypter(mdp):
    return hashlib.sha256(str.encode(mdp)).hexdigest()

# --- INITIALISATION BASE DE DONNÉES (VERSION SÉCURISÉE) ---
DB_PATH = "data_ferme_v8.db" # On change de nom pour éviter l'erreur de l'image 3

def initialiser_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    # Table Utilisateurs
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    # Table RH
    c.execute('CREATE TABLE IF NOT EXISTS rh (date TEXT, nom TEXT, poste TEXT, salaire REAL)')
    # Table Dépenses (Nouvelle structure propre)
    c.execute('''CREATE TABLE IF NOT EXISTS depenses 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, categorie TEXT, article TEXT, 
                  quantite REAL, unite TEXT, prix_unitaire REAL, total REAL)''')
    # Table Production
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, parcelle TEXT, produit TEXT, 
                  quantite REAL, unite TEXT, statut TEXT)''')
    
    # Création Admin
    c.execute('SELECT COUNT(*) FROM users WHERE username = "admin"')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO users VALUES (?,?,?)', ("admin", crypter("agri2026"), "Administrateur"))
    
    conn.commit()
    return conn

conn = initialiser_db()
c = conn.cursor()

# --- CONNEXION ---
if "connecte" not in st.session_state: st.session_state.connecte = False
if "user_role" not in st.session_state: st.session_state.user_role = None

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
        else: st.error("Erreur d'identifiants")
    st.stop()

# --- DESIGN MENU (STYLE PHOTO SMARTPHONE) ---
st.markdown("""
    <style>
    div.stButton > button { 
        height: 100px; border-radius: 15px; background-color: white; 
        color: #333; font-weight: bold; border: 1px solid #ddd;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover { border-color: #2E7D32; color: #2E7D32; }
    </style>
    """, unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page = "Accueil"

# Navigation
cols = st.columns(5) if st.session_state.user_role == "Administrateur" else st.columns(3)
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

# --- PAGES ---
if st.session_state.page == "Finances":
    st.subheader("💰 Bilan des Dépenses")
    # Formulaire simplifié
    with st.expander("➕ Noter une dépense"):
        with st.form("dep"):
            cat = st.selectbox("Type", ["Intrants", "Matériel", "Transport"])
            art = st.text_input("Article (Ex: Engrais)")
            qte = st.number_input("Quantité", min_value=0.0)
            pu = st.number_input("Prix Unitaire", min_value=0.0)
            if st.form_submit_button("Enregistrer"):
                c.execute("INSERT INTO depenses (date, categorie, article, quantite, unite, prix_unitaire, total) VALUES (?,?,?,?,?,?,?)",
                          (date.today().strftime("%d/%m/%Y"), cat, art, qte, "Unité", pu, qte*pu))
                conn.commit()
                st.rerun()
    
    # Affichage
    df = pd.read_sql_query("SELECT * FROM depenses ORDER BY id DESC", conn)
    if not df.empty:
        st.dataframe(df.drop(columns=['id']), use_container_width=True)
        st.metric("Total", f"{df['total'].sum()} FCFA")

elif st.session_state.page == "Réglages":
    if st.button("Se déconnecter"):
        st.session_state.connecte = False
        st.rerun()

else:
    st.info(f"Bienvenue {st.session_state.username}. Cliquez sur une icône pour travailler.")
