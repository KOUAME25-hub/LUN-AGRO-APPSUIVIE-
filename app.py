import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import streamlit.components.v1 as components

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

# Base de données unique
DB_NAME = "lun_agro_v2026_final.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, 
                  provenance TEXT, superficie TEXT, lieu TEXT, qte_rec REAL, dechets REAL, 
                  qte_livrable REAL, montant REAL, mode_paiement TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS phyto 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, produit TEXT, cible TEXT, 
                  parcelle TEXT, dose TEXT, applicateur TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS formation 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, theme TEXT, type_cat TEXT, stagiaire TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- MENU LATÉRAL (ICÔNES) ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")

if
