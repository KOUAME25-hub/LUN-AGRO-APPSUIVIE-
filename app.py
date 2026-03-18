import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import date
from io import BytesIO
from fpdf import FPDF # Importation corrigée

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
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, poste TEXT, contact TEXT, salaire_base REAL, date_embauche TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS rh_paie 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, mois TEXT, montant_verse REAL, date_paiement TEXT)''')
    c.execute('CREATE TABLE IF NOT EXISTS production (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, montant REAL)')
    
    c.execute('SELECT COUNT(*) FROM users WHERE username = "admin"')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO users VALUES (?,?,?)', ("admin", crypter("agri2026"), "Administrateur"))
    conn.commit()
    return conn

conn = initialiser_db()
cursor = conn.cursor()

# --- SÉCURITÉ ---
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
cols = st.columns(5 if st.session_state.user_role == "Administrateur" else 3)

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

# --- LOGIQUE RH ---
if st.session_state.page == "RH":
    st.title("👥 Ressources Humaines")
    t1, t2, t3 = st.tabs(["➕ Ajouter", "💸 Payer", "📋 Fiches PDF"])
    
    with t1:
        with st.form("f_rh"):
            n = st.text_input("Nom"); post = st.selectbox("Poste", ["Ouvrier", "Gardien", "Chef"])
            sal = st.number_input("Salaire (FCFA)", min_value=0)
            if st.form_submit_button("Enregistrer"):
                cursor.execute("INSERT INTO rh_personnel (nom, poste, salaire_base, date_embauche) VALUES (?,?,?,?)", (n, post, sal, date.today().strftime("%d/%m/%Y")))
                conn.commit(); st.success("Ajouté")

    with t2:
        df_p = pd.read_sql_query("SELECT nom FROM rh_personnel", conn)
        if not df_p.empty:
            with st.form("f_p"):
                en = st.selectbox("Employé", df_p['nom'])
                m = st.selectbox("Mois", ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])
                mv = st.number_input("Montant versé", min_value=0)
                if st.form_submit_button("Valider Paiement"):
                    cursor.execute("INSERT INTO rh_paie (nom, mois, montant_verse, date_paiement) VALUES (?,?,?,?)", (en, m, mv, date.today().strftime("%d/%m/%Y")))
                    conn.commit(); st.success("Payé")

    with t3:
        df_h = pd.read_sql_query("SELECT * FROM rh_paie ORDER BY id DESC", conn)
        for i, r in df_h.iterrows():
            c_info, c_pdf = st.columns([3, 1])
            c_info.write(f"📄 {r['nom']} - {r['mois']} ({r['montant_verse']} FCFA)")
            
            # Création du PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "LUN-AGRO PRO - FICHE DE PAIE", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.ln(10)
            pdf.cell(200, 10, f"Employé : {r['nom']}", ln=True)
            pdf.cell(200, 10, f"Période : {r['mois']} 2026", ln=True)
            pdf.cell(200, 10, f"Montant : {r['montant_verse']} FCFA", ln=True)
            pdf.cell(200, 10, f"Date : {r['date_paiement']}", ln=True)
            
            c_pdf.download_button("📥 PDF", pdf.output(), f"Paie_{r['nom']}.pdf", "application/pdf", key=f"pdf_{r['id']}")

elif st.session_state.page == "Accueil":
    st.info(f"Session : {st.session_state.username} | Korhogo")

if st.sidebar.button("Déconnexion"):
    st.session_state.connecte = False
    st.rerun()
