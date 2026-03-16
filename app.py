import streamlit as st
import pandas as pd
import sqlite3
import requests
from datetime import date
import io

# --- 1. CONFIGURATION LOGIN ---
UTILISATEUR = "admin"
MOT_DE_PASSE = "agri2026" 

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
    conn = sqlite3.connect('ferme_v4.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS journal (date TEXT, parcelle TEXT, action TEXT, produit TEXT, qte REAL, cout REAL)')
    conn.commit()

    # --- FORMULAIRE ---
    with st.form("saisie"):
        st.subheader("📝 Noter un travail")
        col1, col2 = st.columns(2)
        p = col1.text_input("Parcelle")
        a = col1.selectbox("Action", ["Semis", "Irrigation", "Traitement", "Récolte", "Achat Matériel"])
        prod = col2.text_input("Produit/Matériel")
        qte = col2.number_input("Quantité", min_value=0.0)
        cout = col2.number_input("Coût total", min_value=0.0)
        
        if st.form_submit_button("Enregistrer"):
            c.execute("INSERT INTO journal VALUES (?,?,?,?,?,?)", (date.today().strftime("%Y-%m-%d"), p, a, prod, qte, cout))
            conn.commit()
            st.success("Données enregistrées !")

    # --- ANALYSE DES DÉPENSES (SANS MATPLOTLIB) ---
    st.divider()
    st.subheader("📊 Analyse des Dépenses")
    df = pd.read_sql_query("SELECT * FROM journal", conn)
    
    if not df.empty:
        # Calcul du total par action
        stats = df.groupby('action')['cout'].sum()
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write("**Dépenses par catégorie**")
            st.bar_chart(stats) # Graphique intégré, pas besoin de module externe !
            
        with c2:
            st.metric("Total Général", f"{df['cout'].sum()} FCFA")
            st.write("**Dernières activités**")
            st.table(df[['action', 'cout']].tail(3))

    # --- EXPORT ---
    if not df.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Suivi')
        st.download_button(label="📥 Télécharger l'historique Excel", data=buffer.getvalue(), file_name="rapport_agri.xlsx")
