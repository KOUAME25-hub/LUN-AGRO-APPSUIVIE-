import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import date
from fpdf import FPDF
from io import BytesIO

# --- CONFIGURATION ET STYLE ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

def crypter(mdp):
    return hashlib.sha256(str.encode(mdp)).hexdigest()

# --- BASE DE DONNÉES ---
DB_PATH = "data_ferme_v2.db"

@st.cache_resource
def initialiser_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS stocks (id INTEGER PRIMARY KEY AUTOINCREMENT, article TEXT, quantite REAL, unite TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS rh_paie (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, montant REAL, date_p TEXT)')
    
    c.execute('SELECT COUNT(*) FROM users WHERE username = "admin"')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO users VALUES (?,?,?)', ("admin", crypter("agri2026"), "Administrateur"))
    conn.commit()
    return conn

conn = initialiser_db()
cursor = conn.cursor()

# --- AUTHENTIFICATION ---
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
            st.rerun()
        else:
            st.error("Identifiant ou mot de passe incorrect")
    st.stop()

# --- MENU DE NAVIGATION ---
st.sidebar.title("📌 Menu Principal")
page = st.sidebar.radio("Aller vers :", ["🏠 Accueil", "📦 Stocks Phyto/Engrais", "👥 RH & Paie"])

# --- PAGE ACCUEIL ---
if page == "🏠 Accueil":
    st.title("Bienvenue sur LUN-AGRO PRO")
    st.info("Localisation : Korhogo, Côte d'Ivoire")
    st.write("Utilisez le menu à gauche pour gérer votre exploitation.")

# --- PAGE STOCKS (Nouveau) ---
elif page == "📦 Stocks Phyto/Engrais":
    st.title("📦 Gestion des Produits Phytosanitaires & Engrais")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Ajouter/Mettre à jour")
        with st.form("form_stock"):
            nom_art = st.selectbox("Article", ["Urée", "NPK", "Herbicide", "Fongicide", "Insecticide"])
            qte = st.number_input("Quantité", min_value=0.0)
            unit = st.selectbox("Unité", ["Sacs", "Litres", "Kg"])
            if st.form_submit_button("Enregistrer"):
                cursor.execute("INSERT INTO stocks (article, quantite, unite) VALUES (?,?,?)", (nom_art, qte, unit))
                conn.commit()
                st.success("Stock mis à jour !")
    
    with col2:
        st.subheader("État des lieux")
        df_s = pd.read_sql_query("SELECT article as Article, SUM(quantite) as Total, unite as Unité FROM stocks GROUP BY article", conn)
        if not df_s.empty:
            st.dataframe(df_s, use_container_width=True)
        else:
            st.warning("Aucun stock enregistré.")

# --- PAGE RH & PAIE ---
elif page == "👥 RH & Paie":
    st.title("👥 Ressources Humaines")
    
    with st.form("form_paie"):
        nom_emp = st.text_input("Nom de l'employé")
        salaire = st.number_input("Montant (FCFA)", min_value=0)
        if st.form_submit_button("Générer Bulletin"):
            if nom_emp and salaire > 0:
                d_paie = date.today().strftime("%d/%m/%Y")
                cursor.execute("INSERT INTO rh_paie (nom, montant, date_p) VALUES (?,?,?)", (nom_emp, salaire, d_paie))
                conn.commit()
                
                # Génération du PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(200, 10, "LUN-AGRO PRO - BULLETIN DE PAIE", ln=True, align="C")
                pdf.ln(10)
                pdf.set_font("Arial", "", 12)
                pdf.cell(200, 10, f"Employé : {nom_emp}", ln=True)
                pdf.cell(200, 10, f"Salaire : {salaire} FCFA", ln=True)
                pdf.cell(200, 10, f"Date : {d_paie}", ln=True)
                
                # Correction : utiliser BytesIO pour le buffer
                pdf_bytes = BytesIO(pdf.output(dest='S').encode('latin-1'))
                
                st.download_button(
                    label="📥 Télécharger PDF",
                    data=pdf_bytes,
                    file_name=f"Paie_{nom_emp}.pdf",
                    mime="application/pdf"
                )
                st.success("Paiement enregistré !")

if st.sidebar.button("🚪 Déconnexion"):
    st.session_state.connecte = False
    st.rerun()
