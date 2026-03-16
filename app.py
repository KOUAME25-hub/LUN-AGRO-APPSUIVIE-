import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# --- CONFIGURATION ET BASE DE DONNÉES ---
st.set_page_config(page_title="AgriPro Digital", layout="wide", page_icon="🚜")

conn = sqlite3.connect('ferme_v2.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS journal (date TEXT, parcelle TEXT, action TEXT, produit TEXT, quantite REAL, cout REAL, notes TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS stocks (produit TEXT PRIMARY KEY, quantite_restante REAL, unite TEXT)')
conn.commit()

st.title("🚜 AgriPro : Gestion Complète")

# --- BARRE LATÉRALE (STOCKS RAPIDES) ---
st.sidebar.header("📦 État des Stocks")
df_stock = pd.read_sql_query("SELECT * FROM stocks", conn)
if not df_stock.empty:
    for index, row in df_stock.iterrows():
        st.sidebar.write(f"**{row['produit']}** : {row['quantite_restante']} {row['unite']}")
else:
    st.sidebar.info("Aucun stock enregistré.")

# --- ONGLETS PRINCIPAUX ---
tab1, tab2, tab3 = st.tabs(["📝 Interventions", "💰 Finances", "⚙️ Paramètres Stocks"])

# --- ONGLET 1 : SAISIE DES TRAVAUX ---
with tab1:
    with st.form("form_inter"):
        col1, col2 = st.columns(2)
        with col1:
            d = st.date_input("Date", date.today())
            p = st.selectbox("Parcelle", ["Parcelle A", "Parcelle B", "Serre 1"])
            a = st.selectbox("Action", ["Semis", "Irrigation", "Traitement", "Récolte", "Vente"])
        with col2:
            prod = st.text_input("Produit utilisé / vendu", "Ex: Urée")
            qte = st.number_input("Quantité (kg/L/Unités)", min_value=0.0)
            prix = st.number_input("Coût ou Revenu total (FCFA/€)", min_value=0.0)
        
        n = st.text_area("Observations")
        
        if st.form_submit_button("Enregistrer l'activité"):
            c.execute("INSERT INTO journal VALUES (?,?,?,?,?,?,?)", (d, p, a, prod, qte, prix, n))
            # Mise à jour automatique du stock si c'est un produit connu
            c.execute("UPDATE stocks SET quantite_restante = quantite_restante - ? WHERE produit = ?", (qte, prod))
            conn.commit()
            st.success("Activité et stocks mis à jour !")
            st.rerun()

    st.subheader("📅 Dernières activités")
    df_hist = pd.read_sql_query("SELECT * FROM journal ORDER BY date DESC LIMIT 10", conn)
    st.dataframe(df_hist, use_container_width=True)

# --- ONGLET 2 : FINANCES ---
with tab2:
    st.subheader("📊 Résumé Financier")
    df_fin = pd.read_sql_query("SELECT action, SUM(cout) as Total FROM journal GROUP BY action", conn)
    if not df_fin.empty:
        ventes = df_fin[df_fin['action'] == 'Vente']['Total'].sum()
        depenses = df_fin[df_fin['action'] != 'Vente']['Total'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Revenus", f"{ventes} FCFA")
        c2.metric("Dépenses", f"{depenses} FCFA", delta_color="inverse")
        c3.metric("Bénéfice Net", f"{ventes - depenses} FCFA")
        
        st.bar_chart(df_fin.set_index('action'))

# --- ONGLET 3 : RÉGLAGES STOCKS ---
with tab3:
    st.subheader("➕ Ajouter du stock initial")
    with st.form("add_stock"):
        nom_p = st.text_input("Nom du produit (ex: NPK, Semence Maïs)")
        qte_p = st.number_input("Quantité en stock", min_value=0.0)
        uni_p = st.selectbox("Unité", ["kg", "L", "Sacs", "Plants"])
        if st.form_submit_button("Ajouter au magasin"):
            c.execute("INSERT OR REPLACE INTO stocks VALUES (?,?,?)", (nom_p, qte_p, uni_p))
            conn.commit()
            st.rerun()
