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

# --- INITIALISATION BASE DE DONNÉES ---
DB_PATH = "data_ferme_permanente.db"

def initialiser_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS rh_personnel (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, salaire REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS rh_paie (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, montant REAL, date_p TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS stocks (id INTEGER PRIMARY KEY AUTOINCREMENT, article TEXT, quantite REAL, unite TEXT)')
    
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
            st.session_state.connecte, st.session_state.user_role, st.session_state.username = True, res[1], u
            st.rerun()
    st.stop()

# --- NAVIGATION ---
if "page" not in st.session_state: st.session_state.page = "Accueil"
menu_items = {"🏠 Accueil": "Accueil", "🌱 Production": "Production", "💰 Finances": "Finances"}

if st.session_state.user_role == "Administrateur":
    menu_items["👥 RH"] = "RH"
    menu_items["⚙️ Réglages"] = "Réglages"

# Utilisation d'une boucle corrigée (Solution Photo 2)
cols = st.columns(len(menu_items))
for i, (label, target) in enumerate(menu_items.items()):
    if cols[i].button(label, use_container_width=True): # Solution Photo 1 (Parenthèse fermée)
        st.session_state.page = target # Solution Photo 4 (Indentation correcte)

st.divider()

# --- LOGIQUE RH & PDF ---
if st.session_state.page == "RH":
    st.title("👥 Gestion RH")
    nom = st.text_input("Nom de l'employé")
    sal = st.number_input("Montant Salaire (FCFA)", min_value=0)
    
    if st.button("Enregistrer & Générer Fiche"):
        if nom and sal > 0:
            date_jour = date.today().strftime("%d/%m/%Y")
            cursor.execute("INSERT INTO rh_paie (nom, montant, date_p) VALUES (?,?,?)", (nom, sal, date_jour))
            conn.commit()
            
            # Génération PDF propre
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "LUN-AGRO PRO - BULLETIN DE PAIE", ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("Arial", "", 12)
            pdf.cell(200, 10, f"Employé : {nom}", ln=True)
            pdf.cell(200, 10, f"Montant : {sal} FCFA", ln=True)
            pdf.cell(200, 10, f"Date de paiement : {date_jour}", ln=True)
            
            st.success("Données enregistrées !")
            st.download_button("📥 Télécharger le PDF", pdf.output(dest='S'), f"Paie_{nom}.pdf", "application/pdf")

elif st.session_state.page == "Accueil":
    st.info(f"Bienvenue {st.session_state.username} | Ville : Korhogo")

if st.sidebar.button("🚪 Déconnexion"):
    st.session_state.connecte = False
    st.rerun()
