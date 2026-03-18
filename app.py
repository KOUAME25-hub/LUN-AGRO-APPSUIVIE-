import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import streamlit.components.v1 as components

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

# Base de données unique
DB_NAME = "lun_agro_v2026_final.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    # Table Production (Détaillée)
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, 
                  provenance TEXT, superficie TEXT, lieu TEXT, qte_rec REAL, dechets REAL, 
                  qte_livrable REAL, montant REAL, mode_paiement TEXT)''')
    # Table Phyto
    c.execute('''CREATE TABLE IF NOT EXISTS phyto 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, produit TEXT, cible TEXT, 
                  parcelle TEXT, dose TEXT, applicateur TEXT)''')
    # Table Agenda
    c.execute('''CREATE TABLE IF NOT EXISTS agenda 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, tache TEXT, responsable TEXT, statut TEXT)''')
    # Table Formation
    c.execute('''CREATE TABLE IF NOT EXISTS formation 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, nom_stagiaire TEXT, ecole TEXT, theme TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- MENU LATÉRAL ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# Navigation par boutons individuels (Plus stable)
if st.sidebar.button("🏠 Accueil", use_container_width=True): st.session_state.page = "Accueil"
if st.sidebar.button("📅 Agenda", use_container_width=True): st.session_state.page = "Agenda"
if st.sidebar.button("🌱 Production", use_container_width=True): st.session_state.page = "Production"
if st.sidebar.button("🧪 Phyto", use_container_width=True): st.session_state.page = "Phyto"
if st.sidebar.button("💰 Finances", use_container_width=True): st.session_state.page = "Finances"
if st.sidebar.button("📚 Formation", use_container_width=True): st.session_state.page = "Formation"
if st.sidebar.button("☁️ Météo", use_container_width=True): st.session_state.page = "Météo"

# --- LOGIQUE DES PAGES ---

# 1. ACCUEIL
if st.session_state.page == "Accueil":
    st.title("🚜 Bienvenue sur LUN-AGRO PRO")
    st.success("Votre centre de gestion agricole à Korhogo est prêt.")
    st.info("Cliquez sur les menus à gauche pour commencer l'enregistrement.")

# 2. AGENDA
elif st.session_state.page == "Agenda":
    st.title("📅 Agenda & Travaux")
    with st.form("f_age"):
        t = st.text_input("Travail à effectuer")
        r = st.text_input("Responsable")
        if st.form_submit_button("Ajouter"):
            conn.execute("INSERT INTO agenda (date, tache, responsable, statut) VALUES (?,?,?,?)",
                         (date.today().strftime("%d/%m/%Y"), t, r, "En cours"))
            conn.commit(); st.rerun()
    st.write("### Travaux en cours")
    st.dataframe(pd.read_sql_query("SELECT * FROM agenda ORDER BY id DESC", conn), use_container_width=True)

# 3. PRODUCTION (Réglages détaillés rétablis)
elif st.session_state.page == "Production":
    st.title("🌱 Suivi de la Production")
    tab1, tab2, tab3 = st.tabs(["🆕 Semis", "🧺 Récolte", "💵 Vente"])
    
    with tab1:
        with st.form("f_sem"):
            c1, c2 = st.columns(2)
            p = c1.text_input("Produit")
            s = c2.text_input("Superficie")
            prov = c1.text_input("Provenance semences")
            if st.form_submit_button("Enregistrer Semis"):
                conn.execute("INSERT INTO production (date, type, produit, superficie, provenance) VALUES (?,?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Semis", p, s, prov))
                conn.commit(); st.success("Semis enregistré !")

    with tab2:
        with st.form("f_rec"):
            c1, c2 = st.columns(2)
            p_r = c1.text_input("Produit récolté")
            q_r = c2.number_input("Quantité récoltée", min_value=0.0)
            dech = c1.number_input("Pertes/Déchets", min_value=0.0)
            if st.form_submit_button("Enregistrer Récolte"):
                conn.execute("INSERT INTO production (date, type, produit, qte_rec, dechets, qte_livrable) VALUES (?,?,?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Récolte", p_r, q_r, dech, q_r-dech))
                conn.commit(); st.success("Récolte enregistrée !")

    with tab3:
        with st.form("f_ven"):
            c1, c2 = st.columns(2)
            p_v = c1.text_input("Produit vendu")
            m = c2.number_input("Montant (FCFA)", min_value=0.0)
            if st.form_submit_button("Valider Vente"):
                conn.execute("INSERT INTO production (date, type, produit, montant) VALUES (?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Vente", p_v, m))
                conn.commit(); st.success("Vente enregistrée !")

# 4. PHYTO
elif st.session_state.page == "Phyto":
    st.title("🧪 Traitements Phytosanitaires")
    with st.form("f_phy"):
        p = st.text_input("Produit utilisé")
        c = st.text_input("Cible (Ravageur)")
        if st.form_submit_button("Enregistrer"):
            conn.execute("INSERT INTO phyto (date, produit, cible) VALUES (?,?,?)",
                         (date.today().strftime("%d/%m/%Y"), p, c))
            conn.commit(); st.success("Traitement enregistré !")

# 5. FINANCES
elif st.session_state.page == "Finances":
    st.title("💰 Suivi Financier")
    total = pd.read_sql_query("SELECT SUM(montant) FROM production WHERE type='Vente'", conn).iloc[0,0] or 0
    st.metric("Total des Revenus", f"{total:,.0f} FCFA")
    st.dataframe(pd.read_sql_query("SELECT date, produit, montant FROM production WHERE type='Vente'", conn))

# 6. FORMATION (Bibliothèques & Stagiaires)
elif st.session_state.page == "Formation":
    st.title("📚 Centre de Formation")
    v_tab, p_tab, s_tab = st.tabs(["🎥 Vidéos", "📖 Bibliothèque Physique", "🧑‍🎓 Stagiaires"])
    
    with v_tab:
        cat = st.selectbox("Thème :", ["Produits phytosanitaires", "Gestion agricole", "Économie agricole", "Technologies agricoles", "Rédaction de rapport de stage"])
        links = {
            "Produits phytosanitaires": "https://www.youtube.com/watch?v=kY97_iX2P-w",
            "Gestion agricole": "https://www.youtube.com/watch?v=FjC6F-GIsdY",
            "Économie agricole": "https://www.youtube.com/watch?v=YmXAn2OInm8",
            "Technologies agricoles": "https://www.youtube.com/watch?v=q6bKId6-E-0",
            "Rédaction de rapport de stage": "https://www.youtube.com/watch?v=q0-N64G3rIs"
        }
        st.video(links[cat])

    with p_tab:
        st.info("Ouvrages disponibles au bureau de la ferme.")
        st.write("- Manuel Phytosanitaire\n- Guide de Gestion Agricole")

    with s_tab:
        st.subheader("🎓 Inscription Stagiaire")
        with st.form("f_stag"):
            nom = st.text_input("Nom")
            ecole = st.text_input("École")
            if st.form_submit_button("Enregistrer"):
                conn.execute("INSERT INTO formation (date, nom_stagiaire, ecole) VALUES (?,?,?)", (date.today().strftime("%d/%m/%Y"), nom, ecole))
                conn.commit(); st.success("Stagiaire ajouté !")

# 7. MÉTÉO
elif st.session_state.page == "Météo":
    st.title("☁️ Météo Korhogo")
    components.html('<iframe src="https://www.meteoblue.com/fr/meteo/widget/three/korhogo_c%c3%b4te-d%27ivoire_2286420?geoloc=fixed&days=4&tempunit=CELSIUS&layout=light" frameborder="0" style="width: 100%; height: 600px"></iframe>', height=620)
