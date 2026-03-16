import streamlit as st
import pandas as pd
import sqlite3
import requests
from datetime import date

# --- CONFIGURATION MÉTÉO ---
# J'utilise une ville par défaut, vous pourrez la changer plus tard
VILLE = "Abidjan" 
API_KEY = "8f36c53e020556637e7225c5d0705018" # Clé de test gratuite

def obtenir_meteo(ville):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ville}&appid={API_KEY}&units=metric&lang=fr"
        res = requests.get(url).json()
        return {
            "temp": res['main']['temp'],
            "hum": res['main']['humidity'],
            "desc": res['weather'][0]['description'],
            "icon": res['weather'][0]['icon']
        }
    except:
        return None

# --- INITIALISATION APP ---
st.set_page_config(page_title="AgriSmart Pro", layout="wide", page_icon="🌤️")

# --- AFFICHAGE MÉTÉO EN HAUT ---
meteo = obtenir_meteo(VILLE)
if meteo:
    col_m1, col_m2, col_m3 = st.columns([1,1,2])
    with col_m1:
        st.metric("Température", f"{meteo['temp']}°C")
    with col_m2:
        st.metric("Humidité", f"{meteo['hum']}%")
    with col_m3:
        st.write(f"**Météo à {VILLE} :** {meteo['desc'].capitalize()}")
        if meteo['hum'] > 80:
            st.warning("⚠️ Humidité forte : Risque de champignons ou maladies.")
        elif meteo['temp'] > 35:
            st.error("🔥 Forte chaleur : Surveillez l'irrigation !")
        else:
            st.success("✅ Conditions favorables pour le travail au champ.")

st.divider()

# --- RESTE DE L'APPLICATION (STOCKS ET JOURNAL) ---
conn = sqlite3.connect('ferme_v3.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS journal (date TEXT, parcelle TEXT, action TEXT, produit TEXT, qte REAL, cout REAL)')
c.execute('CREATE TABLE IF NOT EXISTS stocks (produit TEXT PRIMARY KEY, qte REAL)')
conn.commit()

tab1, tab2 = st.tabs(["📝 Activités & Stocks", "📊 Historique"])

with tab1:
    with st.form("saisie"):
        c1, c2 = st.columns(2)
        p = c1.text_input("Parcelle")
        a = c1.selectbox("Action", ["Semis", "Irrigation", "Traitement", "Récolte"])
        prod = c2.text_input("Produit (Engrais/Semence)")
        qte = c2.number_input("Quantité", min_value=0.0)
        
        if st.form_submit_button("Enregistrer"):
            c.execute("INSERT INTO journal VALUES (?,?,?,?,?,?)", (date.today(), p, a, prod, qte, 0))
            conn.commit()
            st.success("Données enregistrées !")

with tab2:
    df = pd.read_sql_query("SELECT * FROM journal", conn)
    st.dataframe(df, use_container_width=True)
