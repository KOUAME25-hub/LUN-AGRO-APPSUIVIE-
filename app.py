import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import streamlit.components.v1 as components

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

# Base de données
DB_NAME = "lun_agro_v2026_final.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, 
                  lieu TEXT, montant REAL, mode_paiement TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS formation 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, theme TEXT, type_cat TEXT, stagiaire TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- MENU LATÉRAL (ICÔNES) ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# Navigation simplifiée sans erreur de parenthèse
menu_items = {
    "🏠 Accueil": "Accueil",
    "🌱 Production": "Production",
    "📚 Formation": "Formation",
    "💰 Finances": "Finances",
    "☁️ Météo": "Météo"
}

for label, p in menu_items.items
