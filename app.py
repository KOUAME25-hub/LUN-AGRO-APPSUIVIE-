import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import date

# Configuration
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

# Base de données (Nouveau nom pour forcer l'affichage)
DB_NAME = "lun_agro_v2026.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS production (id INTEGER PRIMARY KEY, date TEXT, type TEXT, produit TEXT, lieu TEXT, montant REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS phyto (id INTEGER PRIMARY KEY, date TEXT, produit TEXT, parcelle TEXT)')
    conn.commit()
    return conn

conn = init_db()

# Interface
st.title("🚜 LUN-AGRO PRO")

menu = ["🏠 Accueil", "🌱 Production", "🧪 Phyto", "💰 Finances"]
choix = st.sidebar.selectbox("Menu", menu)

if choix == "🏠 Accueil":
    st.write("### Bienvenue dans votre gestionnaire de ferme.")
    st.info("Sélectionnez une option dans le menu à gauche pour commencer.")

elif choix == "🌱 Production":
    st.subheader("Enregistrement Semis / Récolte / Vente")
    with st.form("prod_form"):
        t = st.selectbox("Type", ["Semé", "Récolte", "Vendu"])
        p = st.text_input("Produit")
        l = st.text_input("Parcelle / Abris")
        m = st.number_input("Montant (si vente)", min_value=0.0)
        if st.form_submit_button("Enregistrer"):
            c = conn.cursor()
            c.execute("INSERT INTO production (date, type, produit, lieu, montant) VALUES (?,?,?,?,?)",
                      (date.today().strftime("%d/%m/%Y"), t, p, l, m))
            conn.commit()
            st.success("Donnée enregistrée !")

    st.write("### Historique")
    df = pd.read_sql_query("SELECT * FROM production", conn)
    st.dataframe(df, use_container_width=True)

elif choix == "🧪 Phyto":
    st.subheader("Traitements Phytosanitaires")
    with st.form("phyto_form"):
        prod = st.text_input("Produit utilisé")
        parc = st.text_input("Parcelle traitée")
        if st.form_submit_button("Valider"):
            c = conn.cursor()
            c.execute("INSERT INTO phyto (date, produit, parcelle) VALUES (?,?,?)",
                      (date.today().strftime("%d/%m/%Y"), prod, parc))
            conn.commit()
            st.rerun()
    st.dataframe(pd.read_sql_query("SELECT * FROM phyto", conn), use_container_width=True)

elif choix == "💰 Finances":
    st.subheader("Bilan des Ventes")
    df = pd.read_sql_query("SELECT SUM(montant) FROM production WHERE type='Vendu'", conn)
    total = df.iloc[0,0] or 0
    st.metric("Total des Revenus", f"{total} FCFA")
