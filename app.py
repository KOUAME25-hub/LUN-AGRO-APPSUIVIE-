import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import date
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

def crypter(mdp):
    return hashlib.sha256(str.encode(mdp)).hexdigest()

# --- BASE DE DONNÉES ---
DB_PATH = "data_ferme_permanente.db"

def initialiser_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    # Tables de sécurité et RH
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS rh (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, nom TEXT, poste TEXT, salaire REAL)')
    # Tables métier (Production et Finances)
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, 
                  superficie TEXT, montant REAL, mode_paiement TEXT)''')
    
    # Création du compte Admin par défaut
    c.execute('SELECT COUNT(*) FROM users WHERE username = "admin"')
    if c.fetchone()[0] == 0:
        admin_pwd = crypter("agri2026")
        c.execute('INSERT INTO users VALUES (?,?,?)', ("admin", admin_pwd, "Administrateur"))
    
    conn.commit()
    return conn

conn = initialiser_db()
cursor = conn.cursor()

# --- SYSTÈME DE CONNEXION ---
if "connecte" not in st.session_state:
    st.session_state.connecte = False

if not st.session_state.connecte:
    st.title("🔐 Connexion LUN-AGRO")
    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")
    if st.button("SE CONNECTER"):
        cursor.execute('SELECT password, role FROM users WHERE username = ?', (u,))
        res = cursor.fetchone()
        if res and res[0] == crypter(p):
            st.session_state.connecte = True
            st.session_state.user_role = res[1]
            st.session_state.username = u
            st.rerun()
        else:
            st.error("Identifiant ou mot de passe incorrect.")
    st.stop()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("🍀 LUN-AGRO PRO")
    st.write(f"Utilisateur : **{st.session_state.username}**")
    st.write(f"Rôle : {st.session_state.user_role}")
    if st.button("Déconnexion"):
        st.session_state.connecte = False
        st.rerun()

# --- NAVIGATION (BOUTONS HORIZONTAUX) ---
if "page" not in st.session_state: st.session_state.page = "Accueil"

n_cols = 5 if st.session_state.user_role == "Administrateur" else 3
cols = st.columns(n_cols)

with cols[0]:
    if st.button("🏠\nAccueil", use_container_width=True): st.session_state.page = "Accueil"
with cols[1]:
    if st.button("🌱\nProduction", use_container_width=True): st.session_state.page = "Production"
with cols[2]:
    if st.button("💰\nFinances", use_container_width=True): st.session_state.page = "Finances"

if st.session_state.user_role == "Administrateur":
    with cols[3]:
        if st.button("👥\nRH", use_container_width=True): st.session_state.page = "RH"
    with cols[4]:
        if st.button("⚙️\nRéglages", use_container_width=True): st.session_state.page = "Réglages"

st.divider()

# --- LOGIQUE DES PAGES ---

# 1. ACCUEIL
if st.session_state.page == "Accueil":
    st.title("🚜 Tableau de Bord - Korhogo")
    st.success(f"Bienvenue, {st.session_state.username} !")
    st.info("Utilisez les icônes ci-dessus pour gérer l'exploitation.")

# 2. PRODUCTION
elif st.session_state.page == "Production":
    st.title("🌱 Gestion de la Production")
    t1, t2 = st.tabs(["🆕 Nouveau Semis", "🧺 Récolte & Vente"])
    with t1:
        with st.form("f_prod"):
            prod = st.text_input("Produit")
            sup = st.text_input("Superficie")
            if st.form_submit_button("Enregistrer"):
                cursor.execute("INSERT INTO production (date, type, produit, superficie) VALUES (?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Semis", prod, sup))
                conn.commit()
                st.success("Données enregistrées.")

# 3. FINANCES (EXPORT EXCEL)
elif st.session_state.page == "Finances":
    st.title("💰 Suivi Financier")
    df_f = pd.read_sql_query("SELECT * FROM production WHERE montant IS NOT NULL", conn)
    st.metric("Total Revenus", f"{df_f['montant'].sum() if not df_f.empty else 0} FCFA")
    
    if not df_f.empty:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_f.to_excel(writer, index=False)
        st.download_button("📊 Télécharger Rapport Excel", output.getvalue(), "Finances_LunAgro.xlsx")
    st.dataframe(df_f, use_container_width=True)

# 4. RÉGLAGES (GESTION COMPTES)
elif st.session_state.page == "Réglages" and st.session_state.user_role == "Administrateur":
    st.subheader("⚙️ Administration des Utilisateurs")
    # Formulaire de création
    with st.expander("➕ Créer un compte"):
        with st.form("new_u"):
            nu = st.text_input("Nom d'utilisateur")
            np = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("CRÉER"):
                try:
                    cursor.execute('INSERT INTO users VALUES (?,?,?)', (nu, crypter(np), "Utilisateur"))
                    conn.commit()
                    st.success("Compte créé.")
                except: st.error("Erreur (identifiant déjà pris).")
    
    # Liste avec suppression (Confirmation popover)
    df_u = pd.read_sql_query("SELECT username, role FROM users", conn)
    for i, r in df_u.iterrows():
        c1, c2, c3 = st.columns([2, 2, 1])
        c1.write(r['username'])
        if r['username'] not in ["admin", st.session_state.username]:
            with c3.popover("❌"):
                if st.button("Confirmer", key=f"del_{r['username']}"):
                    cursor.execute("DELETE FROM users WHERE username = ?", (r['username'],))
                    conn.commit()
                    st.rerun()
