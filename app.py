import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

# Style pour les gros boutons du menu
st.markdown("""
    <style>
    div.stButton > button {
        height: 100px;
        font-size: 18px;
        border-radius: 12px;
        background-color: white;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        border-color: #2E7D32;
        color: #2E7D32;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES ---
conn = sqlite3.connect('ferme_v5.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS rh (date TEXT, nom TEXT, poste TEXT, salaire REAL)')
conn.commit()

# --- NAVIGATION ---
if "page" not in st.session_state:
    st.session_state.page = "🏠 Accueil"

def changer_page(nom):
    st.session_state.page = nom

# --- MENU PRINCIPAL ---
st.title("🚜 Menu de Gestion")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🏠\nAccueil"): changer_page("Accueil")
with col2:
    if st.button("🌱\nProduction"): changer_page("Production")
with col3:
    if st.button("💰\nFinances"): changer_page("Finances")
with col4:
    if st.button("👥\nRH"): changer_page("RH")
with col5:
    if st.button("⚙️\nRéglages"): changer_page("Réglages")

st.divider()

# --- CONTENU DES PAGES
