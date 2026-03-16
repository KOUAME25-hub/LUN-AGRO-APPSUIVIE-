import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import date

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

def crypter(mdp):
    return hashlib.sha256(str.encode(mdp)).hexdigest()

# --- INITIALISATION BASE DE DONNÉES (Version unifiée) ---
DB_PATH = "lun_agro_final_v1.db" 

def initialiser_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS rh (date TEXT, nom TEXT, paie REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS depenses (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, categorie TEXT, article TEXT, total REAL)')
    
    # Table unique pour tout le cycle de production (Semis, Récolte, Vente)
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, 
                  provenance TEXT, superficie TEXT, lieu TEXT, 
                  qte_rec REAL, dechets REAL, pret_livrer REAL,
                  montant_vente REAL, mode_paiement TEXT, moyen_paiement TEXT)''')
    
    # Table Phytosanitaire
    c.execute('''CREATE TABLE IF NOT EXISTS phyto 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, produit TEXT, cible TEXT, parcelle TEXT, dose TEXT, applicateur TEXT)''')

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
menu = ["Accueil", "Production", "Finances", "Phyto", "RH"]
cols = st.columns(len(menu))
