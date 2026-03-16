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
    # Table Production complète
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
    conn.commit()
    return conn

conn = init_db()

# --- MENU LATÉRAL (BOUTONS INDIVIDUELS POUR ÉVITER LES ERREURS) ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

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
    st.title("🚜 Accueil LUN-AGRO PRO")
    st.success("Application de gestion agricole opérationnelle.")
    st.info("Utilisez le menu à gauche pour naviguer dans vos outils.")

# 2. AGENDA
elif st.session_state.page == "Agenda":
    st.title("📅 Planning des travaux")
    with st.form("f_agenda"):
        tache = st.text_input("Travail à effectuer")
        resp = st.text_input("Responsable")
        if st.form_submit_button("Ajouter à l'agenda"):
            conn.execute("INSERT INTO agenda (date, tache, responsable, statut) VALUES (?,?,?,?)",
                         (date.today().strftime("%d/%m/%Y"), tache, resp, "À faire"))
            conn.commit()
            st.success("Tâche ajoutée !")
    st.write("### Liste des travaux")
    st.dataframe(pd.read_sql_query("SELECT * FROM agenda ORDER BY id DESC", conn), use_container_width=True)

# 3. PRODUCTION (DÉTAILLÉE)
elif st.session_state.page == "Production":
    st.title("🌱 Suivi de Production")
    tab1, tab2, tab3 = st.tabs(["🆕 Semis", "🧺 Récolte", "💵 Vente"])
    
    with tab1:
        with st.form("f_semis"):
            c1, c2 = st.columns(2)
            prod = c1.text_input("Produit semé")
            sup = c2.text_input("Superficie (ha/m²)")
            prov = c1.text_input("Provenance des semences")
            lieu = c2.text_input("Parcelle / Lieu")
            if st.form_submit_button("Enregistrer le semis"):
                conn.execute("INSERT INTO production (date, type, produit, provenance, superficie, lieu) VALUES (?,?,?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Semis", prod, prov, sup, lieu))
                conn.commit()
                st.success("Semis enregistré avec succès !")

    with tab2:
        with st.form("f_recolte"):
            c1, c2 = st.columns(2)
            prod_r = c1.text_input("Produit récolté")
            qte = c2.number_input("Quantité totale", min_value=0.0)
            dech = c1.number_input("Déchets / Pertes", min_value=0.0)
            if st.form_submit_button("Enregistrer la récolte"):
                conn.execute("INSERT INTO production (date, type, produit, qte_rec, dechets, qte_livrable) VALUES (?,?,?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Récolte", prod_r, qte, dech, qte-dech))
                conn.commit()
                st.success(f"Récolte enregistrée ! Livrable : {qte-dech}")

    with tab3:
        with st.form("f_vente"):
            c1, c2 = st.columns(2)
            prod_v = c1.text_input("Produit vendu")
            mont = c2.number_input("Montant de la vente (FCFA)", min_value=0.0)
            paye = st.selectbox("Mode de paiement", ["Cash", "Mobile Money", "Virement", "Crédit"])
            if st.form_submit_button("Valider la vente"):
                conn.execute("INSERT INTO production (date, type, produit, montant, mode_paiement) VALUES (?,?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Vente", prod_v, mont, paye))
                conn.commit()
                st.success("Vente enregistrée dans les finances !")

# 4. PHYTO
elif st.session_state.page == "Phyto":
    st.title("🧪 Gestion Phytosanitaire")
    with st.form("f_phyto"):
        c1, c2 = st.columns(2)
        p = c1.text_input("Produit utilisé")
        c = c2.text_input("Cible (Ravageur/Maladie)")
        d = c1.text_input("Dose appliquée")
        app = c2.text_input("Applicateur")
        if st.form_submit_button("Enregistrer le traitement"):
            conn.execute("INSERT INTO phyto (date, produit, cible, dose, applicateur) VALUES (?,?,?,?,?)",
                         (date.today().strftime("%d/%m/%Y"), p, c, d, app))
            conn.commit()
            st.success("Traitement enregistré !")
    st.dataframe(pd.read_sql_query("SELECT * FROM phyto ORDER BY id DESC", conn), use_container_width=True)

# 5. FINANCES
elif st.session_state.page == "Finances":
    st.title("💰 Suivi Financier")
    total_ventes = pd.read_sql_query("SELECT SUM(montant) FROM production WHERE type='Vente'", conn).iloc[0,0] or 0
    st.metric("Total des Revenus", f"{total_ventes:,.0f} FCFA")
    st.write("### Historique des ventes")
    st.dataframe(pd.read_sql_query("SELECT date, produit, montant, mode_paiement FROM production WHERE type='Vente' ORDER BY id DESC", conn), use_container_width=True)

# 6. FORMATION (BIBLIOTHÈQUE AGRICOLE)
elif st.session_state.page == "Formation":
    st.title("📚 Centre de Formation Agricole")
    cat = st.selectbox("Choisir un domaine de formation :", [
        "Produits phytosanitaires", "Gestion agricole", 
        "Économie agricole", "Technologies agricoles", 
        "Rédaction de rapport de stage"
    ])
    
    # Liens YouTube stables et thématiques
    links = {
        "Produits phytosanitaires": "https://www.youtube.com/watch?v=kY97_iX2P-w",
        "Gestion agricole": "https://www.youtube.com/watch?v=FjC6F-GIsdY",
        "Économie agricole": "https://www.youtube.com/watch?v=YmXAn2OInm8",
        "Technologies agricoles": "https://www.youtube.com/watch?v=q6bKId6-E-0",
        "Rédaction de rapport de stage": "https://www.youtube.com/watch?v=q0-N64G3rIs"
    }
    
    st.info(f"Domaine : {cat}")
    st.video(links[cat])
    
    st.divider()
    nom_cert = st.text_input("Nom pour le certificat")
    if st.button("🎓 Générer le Certificat"):
        st.balloons()
        st.markdown(f"<div style='border:5px solid #2E7D32; padding:20px; text-align:center;'><h2>ATTESTATION DE FORMATION</h2><p>LUN-AGRO certifie que <b>{nom_cert}</b> a suivi la formation en {cat}.</p></div>", unsafe_allow_html=True)

# 7. MÉTÉO
elif st.session_state.page == "Météo":
    st.title("☁️ Météo Korhogo")
    components.html('<iframe src="https://www.meteoblue.com/fr/meteo/widget/three/korhogo_c%c3%b4te-d%27ivoire_2286420?geoloc=fixed&days=4&tempunit=CELSIUS&layout=light" frameborder="0" style="width: 100%; height: 600px"></iframe>', height=620)
