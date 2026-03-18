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

# --- MENU NAVIGATION ---
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

# --- PAGE RÉGLAGES AVEC CONFIRMATION DE SUPPRESSION ---
if st.session_state.page == "Réglages" and st.session_state.user_role == "Administrateur":
    st.subheader("⚙️ Gestion des Comptes")
    
    # 1. CRÉATION
    with st.expander("➕ Créer un nouveau compte"):
        with st.form("new_user_form"):
            nu = st.text_input("Identifiant")
            np = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("CRÉER"):
                if nu and np:
                    try:
                        c.execute('INSERT INTO users VALUES (?,?,?)', (nu, crypter(np), "Utilisateur"))
                        conn.commit()
                        st.success(f"Compte {nu} créé !")
                        st.rerun()
                    except: st.error("Identifiant déjà pris.")

    st.divider()

    # 2. LISTE ET SUPPRESSION
    st.write("### 🗑️ Liste des utilisateurs")
    df_users = pd.read_sql_query("SELECT username, role FROM users", conn)
    
    for index, row in df_users.iterrows():
        col_user, col_role, col_action = st.columns([2, 2, 1])
        col_user.write(f"**{row['username']}**")
        col_role.write(f"Accès: {row['role']}")
        
        if row['username'] != "admin" and row['username'] != st.session_state.username:
            # On utilise un "popover" (une petite fenêtre de confirmation)
            with col_action.popover("❌"):
                st.warning(f"Supprimer {row['username']} ?")
                if st.button("Oui, confirmer", key=f"confirm_{row['username']}"):
                    c.execute("DELETE FROM users WHERE username = ?", (row['username'],))
                    conn.commit()
                    st.success("Supprimé !")
                    st.rerun()
        else:
            col_action.write("🛡️ Fixe")

    if st.sidebar.button("Déconnexion"):
        st.session_state.connecte = False
        st.rerun()

elif st.session_state.page == "Accueil":
    st.info(f"Session active : {st.session_state.username} | Ville : Korhogo")
