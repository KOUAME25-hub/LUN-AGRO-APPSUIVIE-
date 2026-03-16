import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import os
from datetime import date

# --- CONFIGURATION PERSISTANTE ---
# Ce dossier permet de garder les données même après une mise à jour sur Streamlit Cloud
DB_PATH = "data_ferme_permanente.db"

def crypter(mdp):
    return hashlib.sha256(str.encode(mdp)).hexdigest()

# --- CONNEXION ET CRÉATION SÉCURISÉE ---
def initialiser_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    # Création des tables si elles n'existent pas (ne supprime rien)
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS rh (date TEXT, nom TEXT, poste TEXT, salaire REAL)')
    
    # Création de l'ADMIN seulement si la table est vide
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        admin_pwd = crypter("agri2026")
        c.execute('INSERT INTO users VALUES (?,?,?)', ("admin", admin_pwd, "Administrateur"))
    
    conn.commit()
    return conn

conn = initialiser_db()
c = conn.cursor()

# --- RESTE DU CODE (SÉCURITÉ & INTERFACE) ---
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
if st.session_state.page == "Réglages" and st.session_state.user_role == "Administrateur":
    st.subheader("⚙️ Gestion des Comptes (Permanent)")
    with st.form("new_user"):
        nu = st.text_input("Nom du nouveau compte")
        np = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("CRÉER"):
            try:
                c.execute('INSERT INTO users VALUES (?,?,?)', (nu, crypter(np), "Utilisateur"))
                conn.commit()
                st.success(f"Compte {nu} créé et sauvegardé !")
            except: st.error("Identifiant déjà pris.")
            
    if st.button("Déconnexion"):
        st.session_state.connecte = False
        st.rerun()

elif st.session_state.page == "RH" and st.session_state.user_role == "Administrateur":
    st.subheader("👥 Ressources Humaines")
    # ... Votre code RH ici ...
