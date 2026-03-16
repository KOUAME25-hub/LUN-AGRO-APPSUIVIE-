import streamlit as st  # Corrigé : 'import' en minuscule
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
    # Table Phyto (Détaillée)
    c.execute('''CREATE TABLE IF NOT EXISTS phyto 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, produit TEXT, cible TEXT, 
                  parcelle TEXT, dose TEXT, applicateur TEXT)''')
    # Table Agenda
    c.execute('''CREATE TABLE IF NOT EXISTS agenda 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, tache TEXT, responsable TEXT, statut TEXT)''')
    # Table Formation / Stagiaires
    c.execute('''CREATE TABLE IF NOT EXISTS formation 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, nom_stagiaire TEXT, ecole TEXT, theme TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- BARRE LATÉRALE ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# Navigation
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
    st.title("🚜 LUN-AGRO PRO - Korhogo")
    st.success("Bienvenue dans votre système de gestion intégrée.")
    st.info("Utilisez le menu à gauche pour enregistrer vos activités.")

# 2. AGENDA
elif st.session_state.page == "Agenda":
    st.title("📅 Planning des Travaux")
    with st.form("f_age"):
        t = st.text_input("Tâche à accomplir")
        r = st.text_input("Responsable")
        if st.form_submit_button("Ajouter au planning"):
            conn.execute("INSERT INTO agenda (date, tache, responsable, statut) VALUES (?,?,?,?)",
                         (date.today().strftime("%d/%m/%Y"), t, r, "En cours"))
            conn.commit()
            st.rerun()
    st.dataframe(pd.read_sql_query("SELECT * FROM agenda ORDER BY id DESC", conn), use_container_width=True)

# 3. PRODUCTION (Onglets détaillés)
elif st.session_state.page == "Production":
    st.title("🌱 Suivi de Production")
    t1, t2, t3 = st.tabs(["🆕 Semis", "🧺 Récolte", "💵 Vente"])
    
    with t1:
        with st.form("f_semis"):
            c1, c2 = st.columns(2)
            p = c1.text_input("Produit")
            s = c2.text_input("Superficie")
            prov = c1.text_input("Provenance semence")
            if st.form_submit_button("Enregistrer Semis"):
                conn.execute("INSERT INTO production (date, type, produit, superficie, provenance) VALUES (?,?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Semis", p, s, prov))
                conn.commit(); st.success("Semis enregistré")

    with t2:
        with st.form("f_recolte"):
            c1, c2 = st.columns(2)
            p_r = c1.text_input("Produit récolté")
            q_r = c2.number_input("Quantité totale", min_value=0.0)
            dech = c1.number_input("Déchets (kg/unités)", min_value=0.0)
            if st.form_submit_button("Enregistrer Récolte"):
                conn.execute("INSERT INTO production (date, type, produit, qte_rec, dechets, qte_livrable) VALUES (?,?,?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Récolte", p_r, q_r, dech, q_r-dech))
                conn.commit(); st.success("Récolte enregistrée")

    with t3:
        with st.form("f_vente"):
            c1, c2 = st.columns(2)
            p_v = c1.text_input("Produit vendu")
            m = c2.number_input("Montant (FCFA)", min_value=0.0)
            mode = st.selectbox("Paiement", ["Cash", "Mobile Money", "Crédit"])
            if st.form_submit_button("Enregistrer Vente"):
                conn.execute("INSERT INTO production (date, type, produit, montant, mode_paiement) VALUES (?,?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Vente", p_v, m, mode))
                conn.commit(); st.success("Vente enregistrée")

# 4. PHYTO
elif st.session_state.page == "Phyto":
    st.title("🧪 Gestion Phytosanitaire")
    with st.form("f_phy"):
        c1, c2 = st.columns(2)
        prod = c1.text_input("Nom du produit")
        cib = c2.text_input("Cible (Ravageur)")
        dos = c1.text_input("Dose")
        if st.form_submit_button("Enregistrer"):
            conn.execute("INSERT INTO phyto (date, produit, cible, dose) VALUES (?,?,?,?)",
                         (date.today().strftime("%d/%m/%Y"), prod, cib, dos))
            conn.commit(); st.rerun()
    st.dataframe(pd.read_sql_query("SELECT * FROM phyto", conn))

# 5. FINANCES
elif st.session_state.page == "Finances":
    st.title("💰 État des Finances")
    rev = pd.read_sql_query("SELECT SUM(montant) FROM production WHERE type='Vente'", conn).iloc[0,0] or 0
    st.metric("Total des Revenus", f"{rev:,.0f} FCFA")
    st.write("### Détail des ventes")
    st.dataframe(pd.read_sql_query("SELECT date, produit, montant, mode_paiement FROM production WHERE type='Vente'", conn))

# 6. FORMATION (Bibliothèques & Stagiaires)
elif st.session_state.page == "Formation":
    st.title("📚 Centre de Formation Agricole")
    
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🎥 Bibliothèque Vidéo", "📖 Bibliothèque Physique", "🧑‍🎓 Stagiaires"])
    
    with sub_tab1:
        cat = st.selectbox("Choisir un thème agricole :", [
            "Produits phytosanitaires", "Gestion agricole", 
            "Économie agricole", "Technologies agricoles", 
            "Rédaction de rapport de stage"
        ])
        links = {
            "Produits phytosanitaires": "https://www.youtube.com/watch?v=FjC6F-GIsdY",
            "Gestion agricole": "https://www.youtube.com/watch?v=kY97_iX2P-w",
            "Économie agricole": "https://www.youtube.com/watch?v=YmXAn2OInm8",
            "Technologies agricoles": "https://www.youtube.com/watch?v=q6bKId6-E-0",
            "Rédaction de rapport de stage": "https://www.youtube.com/watch?v=q0-N64G3rIs"
        }
        st.video(links[cat])

    with sub_tab2:
        st.subheader("📚 Bibliothèque Physique (Bureau)")
        st.write("- Manuel de protection des cultures\n- Guide de l'agriculteur moderne\n- Comptabilité agricole simplifiée")

    with sub_tab3:
        st.subheader("🎓 Suivi des Stagiaires")
        with st.form("f_stag"):
            nom = st.text_input("Nom du stagiaire")
            ecole = st.text_input("École")
            if st.form_submit_button("Inscrire"):
                conn.execute("INSERT INTO formation (date, nom_stagiaire, ecole) VALUES (?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), nom, ecole))
                conn.commit(); st.success("Inscrit !")
        
        st.divider()
        if st.button("🎓 Générer Attestation (Visuel)"):
            st.balloons()
            st.success("Attestation générée avec succès !")

# 7. MÉTÉO
elif st.session_state.page == "Météo":
    st.title("☁️ Météo Korhogo")
    components.html('<iframe src="https://www.meteoblue.com/fr/meteo/widget/three/korhogo_c%c3%b4te-d%27ivoire_2286420?geoloc=fixed&days=4&tempunit=CELSIUS&layout=light" frameborder="0" style="width: 100%; height: 600px"></iframe>', height=620)
