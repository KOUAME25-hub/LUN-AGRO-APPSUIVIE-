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

# --- CONNEXION ET CRÉATION ---
DB_PATH = "data_ferme_permanente.db"

def initialiser_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    # Table Sécurité
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    # Tables RH complètes
    c.execute('''CREATE TABLE IF NOT EXISTS rh_personnel 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, poste TEXT, contact TEXT, salaire_base REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS rh_paie 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, mois TEXT, montant_verse REAL, date_paiement TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS rh_presence 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, date TEXT, statut TEXT)''')
    # Table Métier
    c.execute('CREATE TABLE IF NOT EXISTS production (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, montant REAL)')
    
    conn.commit()
    return conn

conn = initialiser_db()
cursor = conn.cursor()

# --- LOGIN (GARDÉ DE VOTRE CODE) ---
if "connecte" not in st.session_state: st.session_state.connecte = False
if not st.session_state.connecte:
    st.title("🔐
