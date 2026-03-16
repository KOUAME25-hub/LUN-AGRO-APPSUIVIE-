import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import date

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

def crypter(mdp):
    return hashlib.sha256(str.encode(mdp)).hexdigest()

# --- BASE DE DONNÉES ---
conn = sqlite3.connect('ferme_v7.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
# Création Admin par défaut
admin_pwd = crypter("agri2026")
c.execute('INSERT OR IGNORE INTO users VALUES (?,?,?)', ("admin", admin_pwd, "Administrateur"))
c.execute('CREATE TABLE IF NOT EXISTS rh (date TEXT, nom TEXT, poste TEXT, salaire REAL)')
conn.commit()

# --- SYSTEME DE CONNEXION ---
if "connecte" not in st.session_state:
    st.session_state.connecte = False
    st.session_state.user_role = None

if not st.session_state.connecte:
    st.title("🔐 Connexion LUN-AGRO")
    user_input = st.text_input("Identifiant")
    pw_input = st.text_input("Mot de passe", type="password")
    
    if st.button("SE CONNECTER"):
        c.execute('SELECT password, role FROM users WHERE username = ?', (user_input,))
        resultat = c.fetchone()
        if resultat and resultat[0] == crypter(pw_input):
            st.session_state.connecte = True
            st.session_state.username = user_input
            st.session_state.user_role = resultat[1]
            st.rerun()
        else:
            st.error("Identifiants incorrects")
    st.stop()

# --- INTERFACE APRES CONNEXION ---

# Style des boutons
st.markdown("""<style> div.stButton > button { height: 80px; border-radius: 12px; } </style>""", unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page = "🏠 Accueil"

# --- BARRE DE NAVIGATION DYNAMIQUE ---
# On définit les colonnes selon le rôle
if st.session_state.user_role == "Administrateur":
    cols = st.columns(5) # 5 icônes pour l'Admin
else:
    cols = st.columns(3) # Seulement 3 icônes pour les autres

with cols[0]:
    if st.button("🏠\nAccueil"): st.session_state.page = "Accueil"
with cols[1]:
    if st.button("🌱\nProduction"): st.session_state.page = "Production"
with cols[2]:
    if st.button("💰\nFinances"): st.session_state.page = "Finances"

# SECTIONS RÉSERVÉES À L'ADMINISTRATEUR (RH et Réglages)
if st.session_state.user_role == "Administrateur":
    with cols[3]:
        if st.button("👥\nRH"): st.session_state.page = "RH"
    with cols[4]:
        if st.button("⚙️\nRéglages"): st.session_state.page = "Réglages"

st.divider()

# --- GESTION DES PAGES ---

if st.session_state.page == "Accueil":
    st.subheader(f"Bienvenue, {st.session_state.username}")
    st.info(f"Votre rôle : {st.session_state.user_role}")

elif st.session_state.page == "RH" and st.session_state.user_role == "Administrateur":
    st.subheader("👥 Gestion RH (Admin Uniquement)")
    # Formulaire RH...
    with st.form("rh_form"):
        nom = st.text_input("Nom de l'ouvrier")
        paie = st.number_input("Salaire", min_value=0)
        if st.form_submit_button("Enregistrer"):
            c.execute("INSERT INTO rh VALUES (?,?,?,?)", (date.today(), nom, "Ouvrier", paie))
            conn.commit()
            st.success("Payement enregistré")

elif st.session_state.page == "Réglages" and st.session_state.user_role == "Administrateur":
    st.subheader("⚙️ Paramètres & Création de comptes")
    with st.form("creer_compte"):
        new_user = st.text_input("Nouvel Identifiant")
        new_pw = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("CRÉER COMPTE UTILISATEUR"):
            try:
                c.execute('INSERT INTO users VALUES (?,?,?)', (new_user, crypter(new_pw), "Utilisateur"))
                conn.commit()
                st.success(f"Compte '{new_user}' créé avec succès !")
            except: st.error("Erreur ou identifiant déjà pris.")
    
    if st.button("Se déconnecter"):
        st.session_state.connecte = False
        st.rerun()

elif st.session_state.page in ["Production", "Finances"]:
    st.subheader(f"Section {st.session_state.page}")
    st.write("Interface de saisie pour le personnel...")

# Sécurité : Si un simple utilisateur essaie de forcer l'accès aux pages Admin
if st.session_state.page in ["RH", "Réglages"] and st.session_state.user_role != "Administrateur":
    st.session_state.page = "Accueil"
    st.rerun()
