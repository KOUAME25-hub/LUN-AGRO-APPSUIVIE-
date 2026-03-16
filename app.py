import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import date

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

def crypter(mdp):
    return hashlib.sha256(str.encode(mdp)).hexdigest()

# --- INITIALISATION BASE DE DONNÉES ---
DB_PATH = "data_ferme_permanente.db"

def initialiser_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS rh (date TEXT, nom TEXT, poste TEXT, salaire REAL)')
    c.execute('''CREATE TABLE IF NOT EXISTS depenses 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, categorie TEXT, article TEXT, 
                  quantite REAL, unite TEXT, prix_unitaire REAL, total REAL)''')
    # Nouvelle table pour la production
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, parcelle TEXT, produit TEXT, 
                  quantite REAL, unite TEXT, statut TEXT)''')
    
    c.execute('SELECT COUNT(*) FROM users WHERE username = "admin"')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO users VALUES (?,?,?)', ("admin", crypter("agri2026"), "Administrateur"))
    conn.commit()
    return conn

conn = initialiser_db()
c = conn.cursor()

# --- GESTION DE LA CONNEXION (CORRECTIF BUG) ---
if "connecte" not in st.session_state:
    st.session_state.connecte = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None

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
        else:
            st.error("Identifiants incorrects")
    st.stop()

# --- MENU NAVIGATION ---
st.markdown("""<style> div.stButton > button { height: 80px; border-radius: 12px; } </style>""", unsafe_allow_html=True)
cols = st.columns(5) if st.session_state.user_role == "Administrateur" else st.columns(3)

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

# --- PAGE PRODUCTION (NOUVEAU) ---
if st.session_state.page == "Production":
    st.subheader("🌱 Suivi de la Production & Récoltes")
    
    with st.expander("📝 Enregistrer une nouvelle récolte"):
        with st.form("form_prod"):
            c1, c2 = st.columns(2)
            parcelle = c1.text_input("Nom de la Parcelle")
            produit = c2.text_input("Produit (Ex: Maïs, Igname)")
            qte_p = c1.number_input("Quantité récoltée", min_value=0.0)
            u_p = c2.selectbox("Unité", ["Sacs", "Tonnes", "Kg", "Casiers"])
            statut = st.selectbox("Destination", ["Stock", "Vendu", "Consommation"])
            
            if st.form_submit_button("Enregistrer la production"):
                date_s = date.today().strftime("%d/%m/%Y")
                c.execute("INSERT INTO production (date, parcelle, produit, quantite, unite, statut) VALUES (?,?,?,?,?,?)",
                          (date_s, parcelle, produit, qte_p, u_p, statut))
                conn.commit()
                st.success("Récolte enregistrée !")
                st.rerun()

    st.write("### 📋 Historique de Production")
    df_p = pd.read_sql_query("SELECT * FROM production ORDER BY id DESC", conn)
    if not df_p.empty:
        st.dataframe(df_p.drop(columns=['id']), use_container_width=True)
    else:
        st.info("Aucune récolte pour le moment.")

# --- PAGE FINANCES (MISE À JOUR) ---
elif st.session_state.page == "Finances":
    st.subheader("💰 Bilan des Dépenses")
    # ... (Le code précédent des finances reste ici avec l'historique détaillé) ...
    df_dep = pd.read_sql_query("SELECT * FROM depenses ORDER BY id DESC", conn)
    if not df_dep.empty:
        st.metric("TOTAL DÉPENSES", f"{df_dep['total'].sum()} FCFA")
        st.dataframe(df_dep.drop(columns=['id']), use_container_width=True)

# --- PAGE RÉGLAGES (DÉCONNEXION) ---
elif st.session_state.page == "Réglages":
    if st.button("Se déconnecter"):
        st.session_state.connecte = False
        st.rerun()

elif st.session_state.page == "Accueil":
    st.success(f"Bienvenue {st.session_state.username} ! Prêt pour la journée à Korhogo ?")
