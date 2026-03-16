import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

# Nom de base de données
DB_NAME = "lun_agro_final_2026.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, type TEXT, produit TEXT, provenance TEXT, 
                  superficie TEXT, lieu TEXT, qte_rec REAL, dechets REAL, 
                  qte_livrable REAL, montant REAL, mode_paiement TEXT, moyen_paiement TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS phyto 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, produit TEXT, cible TEXT, parcelle TEXT, dose TEXT, applicateur TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- BARRE LATÉRALE (MENU EN ICÔNES) ---
st.sidebar.title("🍀 LUN-AGRO")
st.sidebar.write("---")

# Initialisation de l'état de la page si non présent
if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# Création des boutons d'icônes dans la sidebar
if st.sidebar.button("🏠 Accueil", use_container_width=True):
    st.session_state.page = "Accueil"

if st.sidebar.button("🌱 Production", use_container_width=True):
    st.session_state.page = "Production"

if st.sidebar.button("🧪 Phyto", use_container_width=True):
    st.session_state.page = "Phyto"

if st.sidebar.button("💰 Finances", use_container_width=True):
    st.session_state.page = "Finances"

st.sidebar.write("---")
st.sidebar.caption("LUN-AGRO v1.5 | Korhogo")

# --- LOGIQUE D'AFFICHAGE DES PAGES ---

# 1. ACCUEIL
if st.session_state.page == "Accueil":
    st.title("🚜 Bienvenue sur LUN-AGRO PRO")
    st.success("Système de gestion agricole opérationnel.")
    st.info("Cliquez sur les icônes dans le menu à gauche pour naviguer.")

# 2. PRODUCTION
elif st.session_state.page == "Production":
    st.title("🌱 Gestion de la Production")
    t1, t2, t3 = st.tabs(["🆕 Semer", "🧺 Récolter", "💵 Vendre"])

    with t1:
        with st.form("form_seme"):
            st.subheader("Nouveau Semis")
            c1, c2 = st.columns(2)
            p_s = c1.text_input("Produit Semis")
            prov = c2.text_input("Lieu de Provence (Provenance)")
            sup = c1.text_input("Superficie / Nb de pots")
            lieu = c2.text_input("Parcelle ou Abris")
            d_s = st.date_input("Date de Semis")
            if st.form_submit_button("Enregistrer le Semis"):
                conn.execute("INSERT INTO production (date, type, produit, provenance, superficie, lieu) VALUES (?,?,?,?,?,?)",
                             (d_s.strftime("%d/%m/%Y"), "Semé", p_s, prov, sup, lieu))
                conn.commit()
                st.success("Semis enregistré !")

    with t2:
        with st.form("form_recolte"):
            st.subheader("Nouvelle Récolte")
            c1, c2 = st.columns(2)
            d_r = st.date_input("Date de Récolte")
            lieu_r = c1.text_input("Abris ou Parcelle Récolte")
            p_r = c2.text_input("Produit Récolté")
            q_r = c1.number_input("Quantité Récoltée", min_value=0.0)
            dech = c2.number_input("Déchets", min_value=0.0)
            if st.form_submit_button("Enregistrer la Récolte"):
                q_livre = q_r - dech
                conn.execute("INSERT INTO production (date, type, produit, lieu, qte_rec, dechets, qte_livrable) VALUES (?,?,?,?,?,?,?)",
                             (d_r.strftime("%d/%m/%Y"), "Récolte", p_r, lieu_r, q_r, dech, q_livre))
                conn.commit()
                st.success(f"Récolte enregistrée ! Prêt à livrer : {q_livre}")

    with t3:
        with st.form("form_vente"):
            st.subheader("Nouvelle Vente")
            v1, v2 = st.columns(2)
            d_v = st.date_input("Date de Vente")
            p_v = v1.text_input("Produit Vendu")
            mnt = v2.number_input("Montant Total (FCFA)", min_value=0.0)
            mod = v1.selectbox("Mode de paiement", ["Cash", "Crédit"])
            moyen = v2.selectbox("Moyen de paiement", ["Physique", "Électronique"])
            if st.form_submit_button("Enregistrer la Vente"):
                conn.execute("INSERT INTO production (date, type, produit, montant, mode_paiement, moyen_paiement) VALUES (?,?,?,?,?,?)",
                             (d_v.strftime("%d/%m/%Y"), "Vendu", p_v, mnt, mod, moyen))
                conn.commit()
                st.success("Vente enregistrée !")

    st.divider()
    st.write("### 📝 Historique de Production")
    df = pd.read_sql_query("SELECT * FROM production ORDER BY id DESC", conn)
    st.dataframe(df, use_container_width=True)

# 3. PHYTO
elif st.session_state.page == "Phyto":
    st.title("🧪 Traitements Phytosanitaires")
    with st.form("form_phyto"):
        c1, c2 = st.columns(2)
        pro = c1.text_input("Nom du Produit")
        cib = c2.text_input("Cible (Insecte/Maladie)")
        par = c1.text_input("Parcelle traitée")
        dos = c2.text_input("Dose utilisée")
        app = st.text_input("Nom de l'applicateur")
        if st.form_submit_button("Enregistrer Traitement"):
            conn.execute("INSERT INTO phyto (date, produit, cible, parcelle, dose, applicateur) VALUES (?,?,?,?,?,?)",
                         (date.today().strftime("%d/%m/%Y"), pro, cib, par, dos, app))
            conn.commit()
            st.success("Traitement enregistré !")
    
    st.dataframe(pd.read_sql_query("SELECT * FROM phyto ORDER BY id DESC", conn), use_container_width=True)

# 4. FINANCES
elif st.session_state.page == "Finances":
    st.title("💰 Bilan Financier")
    df_v = pd.read_sql_query("SELECT SUM(montant) FROM production WHERE type='Vendu'", conn)
    total = df_v.iloc[0,0] or 0
    st.metric("Total des Revenus", f"{total} FCFA")
    
    st.write("### Détail des Ventes")
    df_det = pd.read_sql_query("SELECT date, produit, montant, mode_paiement, moyen_paiement FROM production WHERE type='Vendu'", conn)
    st.table(df_det)
