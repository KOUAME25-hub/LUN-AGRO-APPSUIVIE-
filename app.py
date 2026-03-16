import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import streamlit.components.v1 as components

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

# Base de données unique et stable
DB_NAME = "lun_agro_v2026_final.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    # Table Production (Tout le cycle)
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, 
                  provenance TEXT, superficie TEXT, lieu TEXT, qte_rec REAL, dechets REAL, 
                  qte_livrable REAL, montant REAL, mode_paiement TEXT, moyen_paiement TEXT)''')
    # Table Phyto
    c.execute('''CREATE TABLE IF NOT EXISTS phyto 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, produit TEXT, cible TEXT, 
                  parcelle TEXT, dose TEXT, applicateur TEXT)''')
    # Table Agenda
    c.execute('''CREATE TABLE IF NOT EXISTS agenda 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, tache TEXT, responsable TEXT, statut TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- MENU LATÉRAL AVEC ICÔNES ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# Navigation par boutons icônes
if st.sidebar.button("🏠 Accueil", use_container_width=True): st.session_state.page = "Accueil"
if st.sidebar.button("📅 Agenda", use_container_width=True): st.session_state.page = "Agenda"
if st.sidebar.button("🌱 Production", use_container_width=True): st.session_state.page = "Production"
if st.sidebar.button("🧪 Phyto", use_container_width=True): st.session_state.page = "Phyto"
if st.sidebar.button("💰 Finances", use_container_width=True): st.session_state.page = "Finances"
if st.sidebar.button("☁️ Météo", use_container_width=True): st.session_state.page = "Météo"

st.sidebar.write("---")
st.sidebar.caption("Korhogo, Côte d'Ivoire")

# --- LOGIQUE DES PAGES ---

# 1. ACCUEIL
if st.session_state.page == "Accueil":
    st.title("🚜 Bienvenue sur LUN-AGRO PRO")
    st.success("Application de gestion agricole connectée.")
    st.info("Utilisez le menu à gauche pour naviguer dans vos outils.")

# 2. AGENDA
elif st.session_state.page == "Agenda":
    st.title("📅 Agenda & Emploi du Temps")
    with st.form("form_agenda"):
        c1, c2 = st.columns(2)
        tache = c1.text_input("Tâche / Travail à faire")
        resp = c2.text_input("Responsable")
        d_p = st.date_input("Date prévue")
        statut = st.selectbox("Priorité", ["Normal", "Urgent", "Terminé"])
        if st.form_submit_button("Ajouter au planning"):
            conn.execute("INSERT INTO agenda (date, tache, responsable, statut) VALUES (?,?,?,?)",
                         (d_p.strftime("%d/%m/%Y"), tache, resp, statut))
            conn.commit()
            st.rerun()
    st.write("### 📋 Liste des tâches")
    st.dataframe(pd.read_sql_query("SELECT * FROM agenda ORDER BY id DESC", conn), use_container_width=True)

# 3. PRODUCTION (REMIS AU COMPLET)
elif st.session_state.page == "Production":
    st.title("🌱 Gestion de la Production")
    t1, t2, t3 = st.tabs(["🆕 Semer", "🧺 Récolter", "💵 Vendre"])

    with t1:
        with st.form("f_seme"):
            c1, c2 = st.columns(2)
            p_s = c1.text_input("Produit Semis")
            prov = c2.text_input("Lieu de Provenance")
            sup = c1.text_input("Superficie / Nb de pots")
            lieu = c2.text_input("Parcelle ou Abris")
            d_s = st.date_input("Date de Semis")
            if st.form_submit_button("Enregistrer Semis"):
                conn.execute("INSERT INTO production (date, type, produit, provenance, superficie, lieu) VALUES (?,?,?,?,?,?)",
                             (d_s.strftime("%d/%m/%Y"), "Semis", p_s, prov, sup, lieu))
                conn.commit()
                st.rerun()

    with t2:
        with st.form("f_reco"):
            c1, c2 = st.columns(2)
            p_r = c1.text_input("Produit Récolté")
            lieu_r = c2.text_input("Abris ou Parcelle")
            q_r = c1.number_input("Quantité Récoltée", min_value=0.0)
            dech = c2.number_input("Déchets", min_value=0.0)
            d_r = st.date_input("Date de Récolte")
            if st.form_submit_button("Enregistrer Récolte"):
                conn.execute("INSERT INTO production (date, type, produit, lieu, qte_rec, dechets, qte_livrable) VALUES (?,?,?,?,?,?,?)",
                             (d_r.strftime("%d/%m/%Y"), "Récolte", p_r, lieu_r, q_r, dech, q_r-dech))
                conn.commit()
                st.rerun()

    with t3:
        with st.form("f_vent"):
            c1, c2 = st.columns(2)
            p_v = c1.text_input("Produit Vendu")
            mnt = c2.number_input("Montant (FCFA)", min_value=0.0)
            mod = c1.selectbox("Mode de paiement", ["Cash", "Crédit"])
            moyen = c2.selectbox("Moyen", ["Physique", "Électronique"])
            d_v = st.date_input("Date de Vente")
            if st.form_submit_button("Enregistrer Vente"):
                conn.execute("INSERT INTO production (date, type, produit, montant, mode_paiement, moyen_paiement) VALUES (?,?,?,?,?,?)",
                             (d_v.strftime("%d/%m/%Y"), "Vente", p_v, mnt, mod, moyen))
                conn.commit()
                st.rerun()

    st.write("### 📊 Historique Production")
    st.dataframe(pd.read_sql_query("SELECT * FROM production ORDER BY id DESC", conn), use_container_width=True)

# 4. PHYTO (REMIS AU COMPLET)
elif st.session_state.page == "Phyto":
    st.title("🧪 Traitements Phytosanitaires")
    with st.form("f_phy"):
        c1, c2 = st.columns(2)
        pro = c1.text_input("Nom du Produit")
        cib = c2.text_input("Cible (Insecte/Maladie)")
        par = c1.text_input("Parcelle traitée")
        dos = c2.text_input("Dose utilisée")
        app = st.text_input("Applicateur")
        if st.form_submit_button("Enregistrer Traitement"):
            conn.execute("INSERT INTO phyto (date, produit, cible, parcelle, dose, applicateur) VALUES (?,?,?,?,?,?)",
                         (date.today().strftime("%d/%m/%Y"), pro, cib, par, dos, app))
            conn.commit()
            st.rerun()
    st.dataframe(pd.read_sql_query("SELECT * FROM phyto ORDER BY id DESC", conn), use_container_width=True)

# 5. FINANCES (REMIS AU COMPLET)
elif st.session_state.page == "Finances":
    st.title("💰 Suivi Financier")
    df_v = pd.read_sql_query("SELECT SUM(montant) FROM production WHERE type='Vente'", conn)
    total = df_v.iloc[0,0] or 0
    st.metric("TOTAL DES VENTES", f"{total} FCFA")
    st.write("### Détail des revenus")
    st.table(pd.read_sql_query("SELECT date, produit, montant, mode_paiement, moyen_paiement FROM production WHERE type='Vente'", conn))

# 6. MÉTÉO (INTÉGRÉE)
elif st.session_state.page == "Météo":
    st.title("☁️ Météo Korhogo")
    weather_html = """
    <iframe src="https://www.meteoblue.com/fr/meteo/widget/three/korhogo_c%c3%b4te-d%27ivoire_2286420?geoloc=fixed&nocurrent=0&noforecast=0&days=4&tempunit=CELSIUS&windunit=KILOMETER_PER_HOUR&layout=light"  
    frameborder="0" scrolling="NO" allowtransparency="true" style="width: 100%; height: 600px"></iframe>
    """
    components.html(weather_html, height=620)
