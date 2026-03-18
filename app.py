import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import date
from fpdf import FPDF 

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

def crypter(mdp):
    return hashlib.sha256(str.encode(mdp)).hexdigest()

# --- BASE DE DONNÉES ---
DB_PATH = "data_ferme_permanente.db"

def initialiser_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS rh_personnel 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, poste TEXT, salaire_base REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS rh_paie 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, mois TEXT, montant_verse REAL, date_p TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS stocks 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, article TEXT, quantite REAL, unite TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, produit TEXT, montant REAL)''')
    
    c.execute('SELECT COUNT(*) FROM users WHERE username = "admin"')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO users VALUES (?,?,?)', ("admin", crypter("agri2026"), "Administrateur"))
    conn.commit()
    return conn

conn = initialiser_db()
cursor = conn.cursor()

# --- CONNEXION ---
if "connecte" not in st.session_state: st.session_state.connecte = False
if not st.session_state.connecte:
    st.title("🔐 Connexion LUN-AGRO")
    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")
    if st.button("SE CONNECTER"):
        cursor.execute('SELECT password, role FROM users WHERE username = ?', (u,))
        res = cursor.fetchone()
        if res and res[0] == crypter(p):
            st.session_state.connecte, st.session_state.user_role, st.session_state.username = True, res[1], u
            st.rerun()
    st.stop()

# --- NAVIGATION ---
if "page" not in st.session_state: st.session_state.page = "Accueil"
n_cols = 5 if st.session_state.user_role == "Administrateur" else 3
cols = st.columns(n_cols)

with cols[0]:
    if st.button("🏠 Accueil", use_container_width=True): st.session_state.page = "Accueil"
with cols[1]:
    if st.button("🌱 Production", use_container_width=True): st.session_state.page = "Production"
with cols[2]:
    if st.button("💰 Finances", use_container_width=True): st.session_state.page = "Finances"
if st.session_state.user_role == "Administrateur":
    with cols[3]:
        if st.button("👥 RH", use_container_width=True): st.session_state.page = "RH"
    with cols[4]:
        if st.button("⚙️ Réglages", use_container_width=True): st.session_state.page = "Réglages"

st.divider()

# --- PAGE PRODUCTION (AVEC STOCKS) ---
if st.session_state.page == "Production":
    st.title("🌱 Gestion de la Production & Stocks")
    t_prod, t_stock = st.tabs(["📊 Suivi Production", "📦 Stock Engrais/Phyto"])
    
    with t_prod:
        with st.form("f_prod"):
            prod = st.text_input("Produit récolté")
            m_v = st.number_input("Valeur estimée (FCFA)", min_value=0)
            if st.form_submit_button("Enregistrer récolte"):
                cursor.execute("INSERT INTO production (date, produit, montant) VALUES (?,?,?)", 
                             (date.today().strftime("%d/%m/%Y"), prod, m_v))
                conn.commit(); st.success("Production enregistrée")

    with t_stock:
        col_s1, col_s2 = st.columns([1, 2])
        with col_s1:
            st.subheader("Mise à jour")
            with st.form("f_stock"):
                art = st.selectbox("Article", ["Urée", "NPK", "Herbicide", "Fongicide", "Sacs"])
                qte = st.number_input("Quantité", min_value=0.0)
                unit = st.selectbox("Unité", ["Sacs", "Litres", "Kg"])
                if st.form_submit_button("Actualiser le stock"):
                    cursor.execute("INSERT INTO stocks (article, quantite, unite) VALUES (?,?,?)", (art, qte, unit))
                    conn.commit(); st.success("Stock mis à jour")
        with col_s2:
            st.subheader("État actuel des stocks")
            df_s = pd.read_sql_query("SELECT article, SUM(quantite) as Total, unite FROM stocks GROUP BY article", conn)
            st.table(df_s)

# --- PAGE RH (AVEC PDF) ---
elif st.session_state.page == "RH":
    st.title("👥 Ressources Humaines")
    t_rh1, t_rh2 = st.tabs(["➕ Nouveau Personnel", "📄 Bulletins de Paie"])
    
    with t_rh1:
        with st.form("f_rh"):
            nom_e = st.text_input("Nom de l'employé")
            sal_e = st.number_input("Salaire Mensuel (FCFA)", min_value=0)
            if st.form_submit_button("Ajouter"):
                cursor.execute("INSERT INTO rh_personnel (nom, salaire_base) VALUES (?,?)", (nom_e, sal_e))
                cursor.execute("INSERT INTO rh_paie (nom, mois, montant_verse, date_p) VALUES (?,?,?,?)", 
                             (nom_e, "Mars", sal_e, date.today().strftime("%d/%m/%Y")))
                conn.commit(); st.success("Employé ajouté")

    with t_rh2:
        df_h = pd.read_sql_query("SELECT * FROM rh_paie", conn)
        for i, r in df_h.iterrows():
            c1, c2 = st.columns([3, 1])
            c1.write(f"Bulletin : **{r['nom']}** ({r['montant_verse']} FCFA)")
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "LUN-AGRO PRO - KORHOGO", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.ln(10)
            pdf.cell(200, 10, f"Employé : {r['nom']}", ln=True)
            pdf.cell(200, 10, f"Salaire Net : {r['montant_verse']} FCFA", ln=True)
            pdf.cell(200, 10, f"Date de paiement : {r['date_p']}", ln=True)
            
            c2.download_button("📥 PDF", pdf.output(dest='S'), f"Paie_{r['nom']}.pdf", key=f"p_{i}")

elif st.session_state.page == "Accueil":
    st.info(f"Session : {st.session_state.username} | Korhogo, Côte d'Ivoire")
