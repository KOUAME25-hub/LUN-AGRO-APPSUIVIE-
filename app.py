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
    c.execute('CREATE TABLE IF NOT EXISTS depenses (date TEXT, categorie TEXT, libelle TEXT, montant REAL)')
    
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

# --- LOGIQUE DES PAGES ---

# --- PAGE FINANCES (L'intelligence de calcul) ---
if st.session_state.page == "Finances":
    st.subheader("💰 Suivi Financier Global")
    
    # Récupération des données
    df_rh = pd.read_sql_query("SELECT SUM(salaire) as total FROM rh", conn)
    total_salaires = df_rh['total'].iloc[0] or 0
    
    df_dep = pd.read_sql_query("SELECT SUM(montant) as total FROM depenses", conn)
    total_autres = df_dep['total'].iloc[0] or 0
    
    # Affichage des indicateurs
    c1, c2, c3 = st.columns(3)
    c1.metric("Main d'œuvre (RH)", f"{total_salaires} FCFA")
    c2.metric("Autres charges", f"{total_autres} FCFA")
    c3.metric("Dépenses Totales", f"{total_salaires + total_autres} FCFA", delta_color="inverse")

    # Formulaire pour autres dépenses (Engrais, Carburant, etc.)
    with st.expander("➕ Enregistrer une dépense (hors salaires)"):
        with st.form("form_dep"):
            cat = st.selectbox("Catégorie", ["Intrants", "Matériel", "Transport", "Autres"])
            lib = st.text_input("Détails")
            mt = st.number_input("Montant", min_value=0)
            if st.form_submit_button("Valider"):
                c.execute("INSERT INTO depenses VALUES (?,?,?,?)", (date.today(), cat, lib, mt))
                conn.commit()
                st.rerun()

# --- PAGE RH (Saisie des salaires) ---
elif st.session_state.page == "RH" and st.session_state.user_role == "Administrateur":
    st.subheader("👥 Gestion RH & Paye")
    with st.form("rh_form"):
        nom = st.text_input("Nom de l'ouvrier")
        poste = st.selectbox("Poste", ["Permanent", "Journalier"])
        paie = st.number_input("Montant de la paye", min_value=0)
        if st.form_submit_button("Enregistrer le paiement"):
            c.execute("INSERT INTO rh VALUES (?,?,?,?)", (date.today(), nom, poste, paie))
            conn.commit()
            st.success("Paiement ajouté aux finances !")

# --- PAGE RÉGLAGES ---
elif st.session_state.page == "Réglages" and st.session_state.user_role == "Administrateur":
    st.subheader("⚙️ Administration")
    # (Le code de suppression et création reste ici)
    if st.button("Déconnexion"):
        st.session_state.connecte = False
        st.rerun()

elif st.session_state.page == "Accueil":
    st.info(f"Bonjour {st.session_state.username}. Le système est prêt.")
