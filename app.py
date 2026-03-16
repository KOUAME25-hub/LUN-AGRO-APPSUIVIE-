import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import streamlit.components.v1 as components

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

# Base de données
DB_NAME = "lun_agro_v2026_complet.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS production (id INTEGER PRIMARY KEY, date TEXT, type TEXT, produit TEXT, lieu TEXT, montant REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS phyto (id INTEGER PRIMARY KEY, date TEXT, produit TEXT, parcelle TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY, date TEXT, tache TEXT, responsable TEXT, statut TEXT)')
    conn.commit()
    return conn

conn = init_db()

# --- MENU LATÉRAL AVEC ICÔNES ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# Navigation par boutons
if st.sidebar.button("🏠 Accueil", use_container_width=True): st.session_state.page = "Accueil"
if st.sidebar.button("📅 Agenda & Planning", use_container_width=True): st.session_state.page = "Agenda"
if st.sidebar.button("🌱 Production", use_container_width=True): st.session_state.page = "Production"
if st.sidebar.button("🧪 Phyto", use_container_width=True): st.session_state.page = "Phyto"
if st.sidebar.button("💰 Finances", use_container_width=True): st.session_state.page = "Finances"
if st.sidebar.button("☁️ Météo Korhogo", use_container_width=True): st.session_state.page = "Météo"

# --- LOGIQUE DES PAGES ---

if st.session_state.page == "Météo":
    st.title("☁️ Météo en Direct - Korhogo")
    st.write("Prévisions locales pour planifier vos activités agricoles :")
    
    # Intégration directe du Widget Météo (Pas besoin de cliquer sur un lien)
    weather_html = """
    <div id="m-booked-vertical-one-prime-73623"> 
        <div class="weather-customize-city-box"> 
            <iframe src="https://www.meteoblue.com/fr/meteo/widget/three/korhogo_c%c3%b4te-d%27ivoire_2286420?geoloc=fixed&nocurrent=0&noforecast=0&days=4&tempunit=CELSIUS&windunit=KILOMETER_PER_HOUR&layout=light"  
            frameborder="0" scrolling="NO" allowtransparency="true" 
            sandbox="allow-same-origin allow-scripts allow-popups allow-forms" 
            style="width: 100%; height: 600px"></iframe>
        </div>
    </div>
    """
    components.html(weather_html, height=620)

elif st.session_state.page == "Agenda":
    st.title("📅 Agenda & Emploi du Temps")
    with st.form("form_agenda"):
        col1, col2 = st.columns(2)
        tache = col1.text_input("Tâche à faire")
        resp = col2.text_input("Responsable")
        d_p = st.date_input("Date")
        statut = st.selectbox("Statut", ["À faire", "Urgent", "Terminé"])
        if st.form_submit_button("Ajouter"):
            conn.execute("INSERT INTO agenda (date, tache, responsable, statut) VALUES (?,?,?,?)",
                         (d_p.strftime("%d/%m/%Y"), tache, resp, statut))
            conn.commit()
            st.success("Tâche ajoutée !")
    
    df_agenda = pd.read_sql_query("SELECT * FROM agenda ORDER BY id DESC", conn)
    st.dataframe(df_agenda, use_container_width=True)

elif st.session_state.page == "Production":
    st.title("🌱 Production")
    # Remettre ici votre code de production (Semer/Récolter/Vendre)
    st.info("Section Production prête pour vos saisies.")

elif st.session_state.page == "Finances":
    st.title("💰 Finances")
    # Remettre ici votre code de finances
    st.info("Section Finances prête.")

else:
    st.title("🚜 Accueil LUN-AGRO")
    st.write("Bienvenue dans votre outil de gestion.")
    st.info("Sélectionnez une option dans le menu à gauche.")
