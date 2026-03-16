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
    c.execute('CREATE TABLE IF NOT EXISTS production (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, provenance TEXT, superficie TEXT, lieu TEXT, qte_rec REAL, dechets REAL, qte_livrable REAL, montant REAL, mode_paiement TEXT, moyen_paiement TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS phyto (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, produit TEXT, cible TEXT, parcelle TEXT, dose TEXT, applicateur TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, tache TEXT, responsable TEXT, statut TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS formation (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, theme TEXT, type_cat TEXT, lien_video TEXT)')
    conn.commit()
    return conn

conn = init_db()

# --- MENU LATÉRAL ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")
if "page" not in st.session_state: st.session_state.page = "Accueil"

pages = {
    "🏠 Accueil": "Accueil",
    "📅 Agenda": "Agenda",
    "🌱 Production": "Production",
    "🧪 Phyto": "Phyto",
    "💰 Finances": "Finances",
    "📚 Formation": "Formation",
    "☁️ Météo": "Météo"
}

for label, p in pages.items():
    if st.sidebar.button(label, use_container_width=True
