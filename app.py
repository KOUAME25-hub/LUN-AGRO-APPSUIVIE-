import streamlit as st
import pandas as pd
import sqlite3
import requests
from datetime import date

# --- 1. CONFIGURATION DE LA SÉCURITÉ ---
# Vous pouvez changer le mot de passe ici (entre les guillemets)
UTILISATEUR = "admin"
MOT_DE_PASSE = "agri2026" 

def verifier_connexion():
    if "connecte" not in st.session_state:
        st.session_state["connecte"] = False

    if not st.session_state["connecte"]:
        st.title("🔐 Accès Sécurisé - LUN-AGRO")
        user = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if user == UTILISATEUR and password == MOT_DE_PASSE:
                st.session_state["connecte"] = True
                st.rerun()
            else:
                st.error("Identifiants incorrects")
        return False
    return True

# --- 2. LANCEMENT DE L'APPLICATION ---
if verifier_connexion():
    # Bouton de déconnexion dans la barre latérale
    if st.sidebar.button("Se déconnecter"):
        st.session_state["connecte"] = False
        st.rerun()

    # --- LE RESTE DE VOTRE CODE (METEO + STOCKS) ---
    st.title("🚜 Tableau de Bord AgriPro")
    
    # Configuration Météo
    VILLE = "Korhogo" # Vous pouvez changer pour votre ville
    API_KEY = "8f36c53e020556637e7225c5d0705018"

    def obtenir_meteo(ville):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={ville}&appid={API_KEY}&units=metric&lang=fr"
            res = requests.get(url).json()
            return {"temp": res['main']['temp'], "hum": res['main']['humidity'], "desc": res['weather'][0]['description']}
        except: return None

    meteo = obtenir_meteo(VILLE)
    if meteo:
        st.info(f"🌤️ **Météo à {VILLE}** : {meteo['temp']}°C | {meteo['hum']}% humidité ({meteo['desc']})")

    # Base de données
    conn = sqlite3.connect('ferme_secure.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS journal (date TEXT, parcelle TEXT, action TEXT, produit TEXT, qte REAL)')
    conn.commit()

    # Formulaire
    with st.form("saisie_travaux"):
        st.subheader("📝 Enregistrer un travail")
        col1, col2 = st.columns(2)
        p = col1.text_input("Parcelle")
        a = col1.selectbox("Action", ["Semis", "Irrigation", "Traitement", "Récolte"])
        prod = col2.text_input("Produit utilisé")
        qte = col2.number_input("Quantité", min_value=0.0)
        
        if st.form_submit_button("Sauvegarder"):
            c.execute("INSERT INTO journal VALUES (?,?,?,?,?)", (date.today(), p, a, prod, qte))
            conn.commit()
            st.success("Données enregistrées en toute sécurité !")

    # Historique
    st.divider()
    st.subheader("📅 Historique des activités")
    df = pd.read_sql_query("SELECT * FROM journal ORDER BY date DESC", conn)
    st.dataframe(df, use_container_width=True)
