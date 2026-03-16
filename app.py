import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

# Nom de base de données
DB_NAME = "lun_agro_v2026_complet.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    # Table Production
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, lieu TEXT, montant REAL)''')
    # Table Phyto
    c.execute('''CREATE TABLE IF NOT EXISTS phyto 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, produit TEXT, parcelle TEXT)''')
    # Table Agenda / Emploi du temps
    c.execute('''CREATE TABLE IF NOT EXISTS agenda 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, tache TEXT, responsable TEXT, statut TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- BARRE LATÉRALE (MENU AVEC ICÔNES) ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# Menu cliquable
if st.sidebar.button("🏠 Accueil", use_container_width=True): st.session_state.page = "Accueil"
if st.sidebar.button("📅 Agenda & Planning", use_container_width=True): st.session_state.page = "Agenda"
if st.sidebar.button("🌱 Production", use_container_width=True): st.session_state.page = "Production"
if st.sidebar.button("🧪 Phyto", use_container_width=True): st.session_state.page = "Phyto"
if st.sidebar.button("💰 Finances", use_container_width=True): st.session_state.page = "Finances"
if st.sidebar.button("☁️ Météo Korhogo", use_container_width=True): st.session_state.page = "Météo"

st.sidebar.write("---")

# --- LOGIQUE DES PAGES ---

# 1. ACCUEIL
if st.session_state.page == "Accueil":
    st.title("🚜 Bienvenue sur LUN-AGRO PRO")
    st.info("Utilisez le menu à gauche pour gérer votre exploitation.")
    
    # Petit rappel de l'agenda sur l'accueil
    st.write("### 📌 Tâches prioritaires (Agenda)")
    df_plan = pd.read_sql_query("SELECT date, tache FROM agenda WHERE statut='En cours' LIMIT 3", conn)
    if not df_plan.empty:
        st.table(df_plan)
    else:
        st.write("Aucune tâche urgente pour aujourd'hui.")

# 2. AGENDA & EMPLOI DU TEMPS
elif st.session_state.page == "Agenda":
    st.title("📅 Agenda & Emploi du temps")
    
    with st.form("form_agenda"):
        st.write("### Ajouter une tâche au planning")
        col1, col2 = st.columns(2)
        tache = col1.text_input("Travail à faire (ex: Arrosage, Récolte)")
        resp = col2.text_input("Responsable")
        d_prevue = st.date_input("Date prévue")
        statut = st.selectbox("Statut", ["En cours", "Terminé", "Urgent"])
        if st.form_submit_button("Ajouter à l'agenda"):
            conn.execute("INSERT INTO agenda (date, tache, responsable, statut) VALUES (?,?,?,?)",
                         (d_prevue.strftime("%d/%m/%Y"), tache, resp, statut))
            conn.commit()
            st.success("Tâche ajoutée !")

    st.write("### 📝 Emploi du temps de la semaine")
    df_agenda = pd.read_sql_query("SELECT * FROM agenda ORDER BY id DESC", conn)
    st.dataframe(df_agenda, use_container_width=True)

# 3. MÉTÉO (KORHOGO)
elif st.session_state.page == "Météo":
    st.title("☁️ Météo en direct - Korhogo")
    st.write("Voici les prévisions pour planifier vos traitements et arrosages :")
    # Intégration d'une carte météo simple
    st.markdown("""
    <iframe src="https://openweathermap.org/themes/openweathermap/assets/vendor/owm/img/widgets/04n.png" width="0" height="0"></iframe>
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 1px solid #ddd;">
        <h3>🌦️ Korhogo, Côte d'Ivoire</h3>
        <p>Consultez les prévisions détaillées pour l'arrosage ici :</p>
        <a href="https://www.accuweather.com/fr/ci/korhogo/110114/weather-forecast/110114" target="_blank" style="background-color: #2E7D32; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Voir la Météo Agricole</a>
    </div>
    """, unsafe_allow_html=True)

# (Les pages Production, Phyto et Finances restent identiques aux versions précédentes)
elif st.session_state.page == "Production":
    st.title("🌱 Production")
    # Code production...

elif st.session_state.page == "Finances":
    st.title("💰 Finances")
    # Code finances...
