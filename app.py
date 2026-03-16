import streamlit as st
import pandas as pd
import sqlite3
import requests
from datetime import date

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO DASHBOARD", layout="wide")

# Style pour transformer les boutons en grosses cartes
st.markdown("""
    <style>
    div.stButton > button {
        height: 120px;
        font-size: 20px;
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        background-color: white;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    div.stButton > button:hover {
        border-color: #2E7D32;
        color: #2E7D32;
        background-color: #f0fdf4;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION DE LA NAVIGATION ---
if "page" not in st.session_state:
    st.session_state.page = "🏠 Accueil"

def changer_page(nom):
    st.session_state.page = nom

# --- MENU PAR ICÔNES (SÉLECTIONNABLES) ---
st.title("🚜 Menu Principal")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🌱\nProduction"): changer_page("Production")
with col2:
    if st.button("💰\nFinances"): changer_page("Finances")
with col3:
    if st.button("🌤️\nMétéo"): changer_page("Météo")
with col4:
    if st.button("⚙️\nRéglages"): changer_page("Réglages")

st.divider()

# --- AFFICHAGE DU GROUPE SÉLECTIONNÉ ---
st.subheader(f"Section : {st.session_state.page}")

if st.session_state.page == "Production":
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Nom de la Parcelle")
        st.selectbox("Action réalisée", ["Semis", "Récolte", "Traitement"])
    with c2:
        st.number_input("Quantité (kg)", min_value=0)
        if st.button("Enregistrer la production"):
            st.success("Données sauvegardées !")

elif st.session_state.page == "Finances":
    st.metric("Total des dépenses", "150 000 FCFA", "-5%")
    st.bar_chart({"Dépenses": [10, 20, 15, 30]})

elif st.session_state.page == "Météo":
    st.info("📍 Korhogo, Côte d'Ivoire")
    st.write("Température : 31°C")
    st.write("Humidité : 45%")
    st.warning("Conseil : Arrosage recommandé ce soir.")

elif st.session_state.page == "Réglages":
    st.write("Modifier votre profil ou mot de passe.")
    if st.button("Se déconnecter"):
        st.info("Déconnexion...")
