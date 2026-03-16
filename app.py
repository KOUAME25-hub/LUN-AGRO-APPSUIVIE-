import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import streamlit.components.v1 as components

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

# Base de données
DB_NAME = "lun_agro_v2026_final.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    # Table Production
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
    # Table Formation
    c.execute('''CREATE TABLE IF NOT EXISTS formation 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, theme TEXT, type_cat TEXT, stagiaire TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- MENU LATÉRAL (ICÔNES) ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# Navigation (Correction du bug de la boucle)
menu_items = {
    "🏠 Accueil": "Accueil",
    "📅 Agenda": "Agenda",
    "🌱 Production": "Production",
    "🧪 Phyto": "Phyto",
    "💰 Finances": "Finances",
    "📚 Formation": "Formation",
    "☁️ Météo": "Météo"
}

for label, p in menu_items.items():
    if st.sidebar.button(label, use_container_width=True):
        st.session_state.page = p

# --- LOGIQUE DES PAGES ---

# 1. FORMATION (COMPLET : COURS, VIDÉOS, STAGIAIRES)
if st.session_state.page == "Formation":
    st.title("📚 Centre de Formation Agricole")
    
    tab_biblio, tab_cours, tab_certif, tab_stagiaire = st.tabs([
        "🎥 Bibliothèque Vidéo", "📖 Cours & Bibliothèque Physique", "🎓 Certificat", "🧑‍🎓 Formation Stagiaire"
    ])

    with tab_biblio:
        st.subheader("🎥 Formations en Agriculture (Uniquement)")
        cat = st.selectbox("Choisir un domaine :", [
            "Produits phytosanitaires", 
            "Gestion agricole", 
            "Économie agricole", 
            "Technologies agricoles", 
            "Rédaction d'un rapport de stage agricole"
        ])
        
        st.info(f"Ressources disponibles pour : {cat}")
        col1, col2 = st.columns(2)
        
        if "phytosanitaires" in cat:
            with col1: st.video("https://www.youtube.com/watch?v=FjC6F-GIsdY") # Exemple dosage
        elif "Gestion" in cat or "Économie" in cat:
            with col1: st.video("https://www.youtube.com/watch?v=kY97_iX2P-w") # Exemple gestion
        elif "Technologies" in cat:
            with col1: st.video("https://www.youtube.com/watch?v=q6bKId6-E-0")
        elif "rapport" in cat:
            with col1: st.video("https://www.youtube.com/watch?v=q0-N64G3rIs")

    with tab_cours:
        st.subheader("📓 Supports de Cours & Bibliothèque Physique")
        st.write("Documents disponibles au bureau :")
        st.markdown("- *Guide pratique du greffage*\n- *Gestion de trésorerie niveau 1*\n- *Manuel d'utilisation des pulvérisateurs*")
        st.divider()
        st.info("🌐 Cours par vidéoconférence : Prochaine session prévue le 20 mars.")

    with tab_certif:
        st.subheader("🎓 Générateur d'Attestation")
        nom_c = st.text_input("Nom de l'élève")
        theme_c = st.text_input("Thème validé")
        if st.button("Générer le Certificat"):
            st.markdown(f"""
            <div style="border: 5px solid #2E7D32; padding: 20px; text-align: center; background: white; color: black;">
                <h1 style="color: #2E7D32;">CERTIFICAT LUN-AGRO</h1>
                <p>Certifie que <b>{nom_c}</b> a complété la formation :</p>
                <h3>{theme_c}</h3>
                <p>Fait à Korhogo, le {date.today().strftime("%d/%m/%Y")}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab_stagiaire:
        st.subheader("🧑‍🎓 Suivi des Stagiaires")
        with st.form("f_st"):
            st.text_input("Nom du stagiaire")
            st.text_input("École d'origine")
            st.date_input("Date de début")
            if st.form_submit_button("Inscrire Stagiaire"):
                st.success("Stagiaire enregistré dans la base.")

# 2. PRODUCTION
elif st.session_state.page == "Production":
    st.title("🌱 Production")
    # Vos formulaires complets Semis / Récolte / Vente ici...
    st.info("Prêt pour la saisie de vos données de production.")

# 3. MÉTÉO (DIRECTE)
elif st.session_state.page == "Météo":
    st.title("☁️ Météo Korhogo")
    components.html('<iframe src="https://www.meteoblue.com/fr/meteo/widget/three/korhogo_c%c3%b4te-d%27ivoire_2286420?geoloc=fixed&days=4&tempunit=CELSIUS&layout=light" frameborder="0" style="width: 100%; height: 600px"></iframe>', height=620)

else:
    st.title("🚜 Accueil LUN-AGRO")
    st.write("Bienvenue dans votre outil de gestion.")
    st.success("Système opérationnel.")
