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
DB_PATH = "data_ferme_v11.db" 

def initialiser_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS rh (date TEXT, nom TEXT, poste TEXT, salaire REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS depenses (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, categorie TEXT, article TEXT, quantite REAL, unite TEXT, prix_unitaire REAL, total REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS production (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, parcelle TEXT, produit TEXT, quantite REAL, unite TEXT, total_vente REAL)')
    
    c.execute('SELECT COUNT(*) FROM users WHERE username = "admin"')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO users VALUES (?,?,?)', ("admin", crypter("agri2026"), "Administrateur"))
    conn.commit()
    return conn

conn = initialiser_db()
c = conn.cursor()

# --- CONNEXION ---
if "connecte" not in st.session_state: st.session_state.connecte = False
if not st.session_state.connecte:
    st.title("🔐 Connexion LUN-AGRO")
    u, p = st.text_input("Identifiant"), st.text_input("Mot de passe", type="password")
    if st.button("SE CONNECTER"):
        c.execute('SELECT password, role FROM users WHERE username = ?', (u,))
        res = c.fetchone()
        if res and res[0] == crypter(p):
            st.session_state.connecte, st.session_state.user_role, st.session_state.username = True, res[1], u
            st.rerun()
    st.stop()

# --- NAVIGATION ---
if "page" not in st.session_state: st.session_state.page = "Accueil"
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

# --- PAGE FINANCES AMÉLIORÉE ---
if st.session_state.page == "Finances":
    st.subheader("💰 Bilan Financier & Export")

    # Calculs
    df_dep_total = pd.read_sql_query("SELECT SUM(total) FROM depenses", conn).iloc[0,0] or 0
    df_sal_total = pd.read_sql_query("SELECT SUM(salaire) FROM rh", conn).iloc[0,0] or 0
    df_ven_total = pd.read_sql_query("SELECT SUM(total_vente) FROM production WHERE type='Vendu'", conn).iloc[0,0] or 0
    benefice = df_ven_total - (df_dep_total + df_sal_total)

    m1, m2, m3 = st.columns(3)
    m1.metric("Ventes", f"{df_ven_total} FCFA")
    m2.metric("Charges (Dépenses + RH)", f"{df_dep_total + df_sal_total} FCFA")
    m3.metric("Bénéfice Net", f"{benefice} FCFA", delta=f"{benefice}")

    st.divider()

    # --- SECTION EXPORT EXCEL (CSV) ---
    st.write("### 📥 Télécharger vos rapports")
    col1, col2, col3 = st.columns(3)

    # Export Dépenses
    df_exp_dep = pd.read_sql_query("SELECT * FROM depenses", conn)
    csv_dep = df_exp_dep.to_csv(index=False).encode('utf-8')
    col1.download_button("📂 Export Dépenses (Excel)", csv_dep, "depenses_lun_agro.csv", "text/csv")

    # Export Production
    df_exp_prod = pd.read_sql_query("SELECT * FROM production", conn)
    csv_prod = df_exp_prod.to_csv(index=False).encode('utf-8')
    col2.download_button("📂 Export Production (Excel)", csv_prod, "production_lun_agro.csv", "text/csv")

    # Export RH
    df_exp_rh = pd.read_sql_query("SELECT * FROM rh", conn)
    csv_rh = df_exp_rh.to_csv(index=False).encode('utf-8')
    col3.download_button("📂 Export RH (Excel)", csv_rh, "rh_lun_agro.csv", "text/csv")

# --- PAGE PRODUCTION ---
elif st.session_state.page == "Production":
    # (On garde le même code que précédemment pour les 3 onglets)
    st.subheader("🌱 Gestion Production")
    tab1, tab2, tab3 = st.tabs(["🆕 Semer", "🧺 Récolter", "💵 Vendre"])
    # ... (Le
