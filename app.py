import streamlit as st
import pandas as pd
import sqlite3
import requests
from datetime import date
import io

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide", page_icon="📊")

# --- STYLE PERSONNALISÉ (DESIGN) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "connecte" not in st.session_state: st.session_state["connecte"] = False

if not st.session_state["connecte"]:
    st.title("🔐 Accès RH & Gestion")
    user = st.text_input("Identifiant")
    pw = st.text_input("Mot de passe", type="password")
    if st.button("SE CONNECTER"):
        if user == "admin" and pw == "agri2026":
            st.session_state["connecte"] = True
            st.rerun()
else:
    # --- INTERFACE PRO ---
    st.title("📱 Tableau de Bord LUN-AGRO")
    
    # 1. MENU EN ICONES (Comme sur votre photo)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Stocks", "Actifs", help="Gestion des ressources")
    with col2:
        st.metric("👥 Équipe", "5 Membres", help="Suivi du personnel")
    with col3:
        st.metric("📈 Performance", "85%", delta="12%")

    st.divider()

    # 2. PARTIE METEO ET SAISIE
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("🌦️ Météo Locale")
        # Ici le petit module météo simplifié
        st.info("**Korhogo** : 32°C \n\n Ciel dégagé")
        
    with c2:
        st.subheader("📝 Nouvelle Entrée")
        with st.form("main_form"):
            action = st.selectbox("Type d'activité", ["Recrutement", "Formation", "Suivi Champ", "Dépense"])
            note = st.text_area("Description")
            valeur = st.number_input("Montant / Valeur", min_value=0)
            if st.form_submit_button("ENREGISTRER DANS LE SYSTÈME"):
                st.success("Donnée enregistrée avec succès !")

    # 3. GRAPHIQUE DE PERFORMANCE
    st.subheader("📊 Analyse des activités")
    # Simulation de données pour le graphique
    data = pd.DataFrame({'Jours': ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven'], 'Activités': [10, 15, 8, 22, 18]})
    st.line_chart(data.set_index('Jours'))

    if st.sidebar.button("Déconnexion"):
        st.session_state["connecte"] = False
        st.rerun()
