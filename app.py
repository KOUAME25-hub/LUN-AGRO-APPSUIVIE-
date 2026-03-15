import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# --- CONFIGURATION SIMPLE ---
st.set_page_config(page_title="Mon Suivi Agricole", page_icon="🌱")
st.title("🚜 Mon Assistant Agricole")

# Connexion à la base de données
conn = sqlite3.connect('ferme.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS journal (date TEXT, parcelle TEXT, action TEXT, notes TEXT)')
conn.commit()

# --- FORMULAIRE DE SAISIE ---
st.subheader("📝 Noter une activité")
with st.form("formulaire"):
    d = st.date_input("Date", date.today())
    p = st.text_input("Nom de la parcelle", "Parcelle 1")
    a = st.selectbox("Action réalisée", ["Semis", "Irrigation", "Engrais", "Récolte"])
    n = st.text_area("Notes (météo, quantité...)")
    
    if st.form_submit_button("Sauvegarder dans le téléphone"):
        c.execute("INSERT INTO journal VALUES (?,?,?,?)", (d.strftime("%Y-%m-%d"), p, a, n))
        conn.commit()
        st.success("C'est enregistré !")

# --- HISTORIQUE ---
st.divider()
st.subheader("📅 Historique")
df = pd.read_sql_query("SELECT * FROM journal ORDER BY date DESC", conn)
st.dataframe(df, use_container_width=True)
