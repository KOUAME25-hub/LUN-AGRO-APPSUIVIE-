import streamlit as st
import pandas as pd
import sqlite3
import requests
from datetime import date
import io

# --- 1. CONFIGURATION DU LOGIN ---
UTILISATEUR = "LUN-AGRO"
MOT_DE_PASSE = "LUNA2023" 

def verifier_connexion():
    if "connecte" not in st.session_state:
        st.session_state["connecte"] = False
    if not st.session_state["connecte"]:
        st.title("🔐 Connexion - LUN-AGRO")
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

# --- 2. LOGIQUE DE L'APPLICATION ---
if verifier_connexion():
    st.sidebar.success(f"Connecté : {UTILISATEUR}")
    if st.sidebar.button("Se déconnecter"):
        st.session_state["connecte"] = False
        st.rerun()

    st.title("🚜 Mon Assistant AgriPro")
    
    # --- MÉTÉO ---
    VILLE = "Korhogo" 
    API_KEY = "8f36c53e020556637e7225c5d0705018"
    def obtenir_meteo(ville):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={ville}&appid={API_KEY}&units=metric&lang=fr"
            res = requests.get(url).json()
            return {"temp": res['main']['temp'], "hum": res['main']['humidity'], "desc": res['weather'][0]['description']}
        except: return None

    meteo = obtenir_meteo(VILLE)
    if meteo:
        st.info(f"🌤️ **Météo à {VILLE}** : {meteo['temp']}°C | {meteo['hum']}% Humidité")

    # --- BASE DE DONNÉES ---
    conn = sqlite3.connect('ferme_secure.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS journal (date TEXT, parcelle TEXT, action TEXT, produit TEXT, qte REAL)')
    conn.commit()

    # --- FORMULAIRE ---
    with st.form("saisie"):
        st.subheader("📝 Noter un travail")
        col1, col2 = st.columns(2)
        p = col1.text_input("Parcelle")
        a = col1.selectbox("Action", ["Semis", "Irrigation", "Traitement", "Récolte"])
        prod = col2.text_input("Produit")
        qte = col2.number_input("Quantité", min_value=0.0)
        if st.form_submit_button("Enregistrer"):
            c.execute("INSERT INTO journal VALUES (?,?,?,?,?)", (date.today(), p, a, prod, qte))
            conn.commit()
            st.success("Données enregistrées !")

    # --- HISTORIQUE ET EXPORT EXCEL ---
    st.divider()
    st.subheader("📅 Historique et Export")
    df = pd.read_sql_query("SELECT * FROM journal ORDER BY date DESC", conn)
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        # Préparation du fichier Excel en mémoire
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Suivi_Agricole')
        
        st.download_button(
            label="📥 Télécharger l'historique en Excel",
            data=buffer.getvalue(),
            file_name=f"rapport_agri_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
