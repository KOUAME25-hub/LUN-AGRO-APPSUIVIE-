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
# On fixe le nom pour ne plus perdre les données
DB_PATH = "lun_agro_database_finale.db" 

def initialiser_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS rh (date TEXT, nom TEXT, poste TEXT, salaire REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS depenses (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, categorie TEXT, article TEXT, quantite REAL, unite TEXT, prix_unitaire REAL, total REAL)')
    
    # Table Production complète avec TOUS vos champs
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, 
                  type TEXT, 
                  produit TEXT, 
                  provenance TEXT, 
                  superficie_pots TEXT, 
                  parcelle_abris TEXT,
                  qte_recolte REAL, 
                  qte_dechets REAL, 
                  qte_livrable REAL,
                  mode_paiement TEXT, 
                  moyen_paiement TEXT, 
                  total_vente REAL)''')
    
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

# --- PAGE PRODUCTION ---
if st.session_state.page == "Production":
    st.subheader("🌱 Gestion de Production")
    
    t1, t2, t3 = st.tabs(["Semer", "Récolter", "Vendre"])

    with t1:
        with st.form("f_semer"):
            st.markdown("**Formulaire Semis**")
            p_s = st.text_input("Produit Semis")
            prov = st.text_input("Lieu de Provenance")
            d_s = st.date_input("Date de Semis")
            sup = st.text_input("Superficie ou nombre de pots")
            lieu = st.selectbox("Parcelle ou Abris", ["Parcelle 1", "Parcelle 2", "Abris Nord", "Abris Sud"])
            if st.form_submit_button("Enregistrer Semis"):
                c.execute("INSERT INTO production (date, type, produit, provenance, superficie_pots, parcelle_abris) VALUES (?,?,?,?,?,?)", 
                          (d_s.strftime("%d/%m/%Y"), "Semé", p_s, prov, sup, lieu))
                conn.commit()
                st.rerun()

    with t2:
        with st.form("f_recolte"):
            st.markdown("**Formulaire Récolte**")
            d_r = st.date_input("Date de Récolte")
            lieu_r = st.selectbox("Abris ou Parcelle", ["Parcelle 1", "Parcelle 2", "Abris Nord", "Abris Sud"], key="lr")
            p_r = st.text_input("Produit Récolté")
            q_r = st.number_input("Quantité Récoltée", min_value=0.0)
            q_d = st.number_input("Déchets", min_value=0.0)
            if st.form_submit_button("Enregistrer Récolte"):
                c.execute("INSERT INTO production (date, type, produit, parcelle_abris, qte_recolte, qte_dechets, qte_livrable) VALUES (?,?,?,?,?,?,?)", 
                          (d_r.strftime("%d/%m/%Y"), "Récolte", p_r, lieu_r, q_r, q_d, q_r-q_d))
                conn.commit()
                st.rerun()

    with t3:
        with st.form("f_vente"):
            st.markdown("**Formulaire Vente**")
            d_v = st.date_input("Date de vente")
            p_v = st.text_input("Produit vendu")
            m_p = st.selectbox("Mode de paiement", ["Crédit", "Cash"])
            my_p = st.selectbox("Moyen de paiement", ["Électronique", "Physique"])
            val = st.number_input("Montant Total (FCFA)", min_value=0.0)
            if st.form_submit_button("Enregistrer Vente"):
                c.execute("INSERT INTO production (date, type, produit, total_vente, mode_paiement, moyen_paiement) VALUES (?,?,?,?,?,?)", 
                          (d_v.strftime("%d/%m/%Y"), "Vendu", p_v, val, m_p, my_p))
                conn.commit()
                st.rerun()

    st.write("### 📊 Historique détaillé")
    # Cette ligne permet d'afficher TOUTES les données saisies
    df = pd.read_sql_query("SELECT * FROM production ORDER BY id DESC", conn)
    st.dataframe(df, use_container_width=True)

# --- PAGE FINANCES ---
elif st.session_state.page == "Finances":
    st.subheader("💰 Suivi Financier")
    df_v = pd.read_sql_query("SELECT SUM(total_vente) FROM production WHERE type='Vendu'", conn).iloc[0,0] or 0
    st.metric("Total des Ventes", f"{df_v} FCFA")
    st.write("Détails des ventes :")
    df_details_v = pd.read_sql_query("SELECT date, produit, mode_paiement, total_vente FROM production WHERE type='Vendu'", conn)
    st.table(df_details_v)

elif st.session_state.page == "Réglages":
    if st.button("Déconnexion"):
        st.session_state.connecte = False
        st.rerun()                  moyen_paiement TEXT, 
                  total_vente REAL)''')
    
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

# --- PAGE PRODUCTION ---
if st.session_state.page == "Production":
    st.subheader("🌱 Gestion de Production")
    
    t1, t2, t3 = st.tabs(["Semer", "Récolter", "Vendre"])

    with t1:
        with st.form("f_semer"):
            st.markdown("**Formulaire Semis**")
            p_s = st.text_input("Produit Semis")
            prov = st.text_input("Lieu de Provenance")
            d_s = st.date_input("Date de Semis")
            sup = st.text_input("Superficie ou nombre de pots")
            lieu = st.selectbox("Parcelle ou Abris", ["Parcelle 1", "Parcelle 2", "Abris Nord", "Abris Sud"])
            if st.form_submit_button("Enregistrer Semis"):
                c.execute("INSERT INTO production (date, type, produit, provenance, superficie_pots, parcelle_abris) VALUES (?,?,?,?,?,?)", 
                          (d_s.strftime("%d/%m/%Y"), "Semé", p_s, prov, sup, lieu))
                conn.commit()
                st.rerun()

    with t2:
        with st.form("f_recolte"):
            st.markdown("**Formulaire Récolte**")
            d_r = st.date_input("Date de Récolte")
            lieu_r = st.selectbox("Abris ou Parcelle", ["Parcelle 1", "Parcelle 2", "Abris Nord", "Abris Sud"], key="lr")
            p_r = st.text_input("Produit Récolté")
            q_r = st.number_input("Quantité Récoltée", min_value=0.0)
            q_d = st.number_input("Déchets", min_value=0.0)
            if st.form_submit_button("Enregistrer Récolte"):
                c.execute("INSERT INTO production (date, type, produit, parcelle_abris, qte_recolte, qte_dechets, qte_livrable) VALUES (?,?,?,?,?,?,?)", 
                          (d_r.strftime("%d/%m/%Y"), "Récolte", p_r, lieu_r, q_r, q_d, q_r-q_d))
                conn.commit()
                st.rerun()

    with t3:
        with st.form("f_vente"):
            st.markdown("**Formulaire Vente**")
            d_v = st.date_input("Date de vente")
            p_v = st.text_input("Produit vendu")
            m_p = st.selectbox("Mode de paiement", ["Crédit", "Cash"])
            my_p = st.selectbox("Moyen de paiement", ["Électronique", "Physique"])
            val = st.number_input("Montant Total (FCFA)", min_value=0.0)
            if st.form_submit_button("Enregistrer Vente"):
                c.execute("INSERT INTO production (date, type, produit, total_vente, mode_paiement, moyen_paiement) VALUES (?,?,?,?,?,?)", 
                          (d_v.strftime("%d/%m/%Y"), "Vendu", p_v, val, m_p, my_p))
                conn.commit()
                st.rerun()

    st.write("### 📊 Historique détaillé")
    # Cette ligne permet d'afficher TOUTES les données saisies
    df = pd.read_sql_query("SELECT * FROM production ORDER BY id DESC", conn)
    st.dataframe(df, use_container_width=True)

# --- PAGE FINANCES ---
elif st.session_state.page == "Finances":
    st.subheader("💰 Suivi Financier")
    df_v = pd.read_sql_query("SELECT SUM(total_vente) FROM production WHERE type='Vendu'", conn).iloc[0,0] or 0
    st.metric("Total des Ventes", f"{df_v} FCFA")
    st.write("Détails des ventes :")
    df_details_v = pd.read_sql_query("SELECT date, produit, mode_paiement, total_vente FROM production WHERE type='Vendu'", conn)
    st.table(df_details_v)

elif st.session_state.page == "Réglages":
    if st.button("Déconnexion"):
        st.session_state.connecte = False
        st.rerun()
