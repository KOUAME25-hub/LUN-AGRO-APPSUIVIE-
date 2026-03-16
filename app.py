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
    # Tables existantes
    c.execute('CREATE TABLE IF NOT EXISTS production (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, provenance TEXT, superficie TEXT, lieu TEXT, qte_rec REAL, dechets REAL, qte_livrable REAL, montant REAL, mode_paiement TEXT, moyen_paiement TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS phyto (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, produit TEXT, cible TEXT, parcelle TEXT, dose TEXT, applicateur TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, tache TEXT, responsable TEXT, statut TEXT)')
    # Table Formation enrichie
    c.execute('CREATE TABLE IF NOT EXISTS formation (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, theme TEXT, formateur TEXT, participants TEXT, type_formation TEXT, ressource_url TEXT)')
    conn.commit()
    return conn

conn = init_db()

# --- MENU LATÉRAL ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")
if "page" not in st.session_state: st.session_state.page = "Accueil"

pages = {
    "🏠 Accueil": "Accueil",
    "📅 Agenda": "Agenda",
    "🌱 Production": "Production",
    "🧪 Phyto": "Phyto",
    "💰 Finances": "Finances",
    "📚 Formation": "Formation",
    "☁️ Météo": "Météo"
}

for label, p in pages.items():
    if st.sidebar.button(label, use_container_width=True):
        st.session_state.page = p

# --- LOGIQUE DE LA PAGE FORMATION ---
if st.session_state.page == "Formation":
    st.title("📚 Centre de Formation LUN-AGRO")
    
    # Sous-menu en onglets pour organiser les nouvelles sections
    t_cours, t_biblio, t_visio, t_certif, t_stagiaire = st.tabs([
        "📖 Cours", 
        "📚 Bibliothèques", 
        "🎥 Vidéoconférence", 
        "🎓 Certificat", 
        "🧑‍🎓 Stagiaires"
    ])

    with t_cours:
        st.subheader("📓 Supports de Cours")
        with st.form("f_cours"):
            c1, c2 = st.columns(2)
            titre = c1.text_input("Titre du cours")
            cat = c2.selectbox("Catégorie", ["Agronomie", "Gestion", "Sécurité", "Technique"])
            contenu = st.text_area("Résumé du cours ou notes importantes")
            if st.form_submit_button("Publier le cours"):
                conn.execute("INSERT INTO formation (date, theme, formateur, type_formation) VALUES (?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), titre, "Interne", "Cours"))
                conn.commit()
                st.success("Cours enregistré !")

    with t_biblio:
        col_phys, col_vid = st.columns(2)
        with col_phys:
            st.subheader("📚 Bibliothèque Physique")
            st.info("Liste des ouvrages disponibles au bureau de la ferme.")
            # Exemple d'affichage
            st.write("- Manuel du Maïs (Ed. 2024)\n- Guide des produits Phytosanitaires\n- Gestion de trésorerie agricole")
            
        with col_vid:
            st.subheader("🎞️ Bibliothèque Vidéo")
            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # Remplacer par vos liens réels
            url_v = st.text_input("Ajouter un lien vidéo (YouTube/Drive)")
            if st.button("Enregistrer Vidéo"):
                st.success("Lien ajouté à la bibliothèque")

    with t_visio:
        st.subheader("🌐 Cours par Vidéoconférence")
        st.write("Prochaines sessions en direct :")
        c1, c2 = st.columns([2, 1])
        c1.warning("🗓️ Séminaire sur l'irrigation - Mercredi à 10h")
        if c2.button("Rejoindre (Zoom/Meet)"):
            st.write("Lien d'appel : [Cliquer ici](https://meet.google.com)")

    with t_certif:
        st.subheader("🎓 Générateur de Certificats")
        nom_c = st.text_input("Nom du récipiendaire")
        formation_c = st.text_input("Nom de la formation validée")
        if st.button("Générer le Certificat"):
            st.markdown(f"""
            <div style="border: 10px double #2E7D32; padding: 30px; text-align: center; background: white; color: black;">
                <h1 style="color: #2E7D32;">CERTIFICAT DE RÉUSSITE</h1>
                <p>Décerné à <b>{nom_c}</b></p>
                <p>Pour avoir complété avec succès la formation :</p>
                <h3>{formation_c}</h3>
                <p>Fait à Korhogo, le {date.today().strftime("%d/%m/%Y")}</p>
            </div>
            """, unsafe_allow_html=True)

    with t_stagiaire:
        st.subheader("🧑‍🎓 Suivi des Stagiaires")
        with st.form("f_stagiaire"):
            nom_s = st.text_input("Nom du Stagiaire")
            ecole = st.text_input("École / Université")
            periode = st.text_input("Période de stage")
            mission = st.text_area("Objectifs du stage")
            if st.form_submit_button("Inscrire Stagiaire"):
                conn.execute("INSERT INTO formation (date, theme, formateur, participants, type_formation) VALUES (?,?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Stage: "+mission, ecole, nom_s, "Stagiaire"))
                conn.commit()
                st.success("Stagiaire enregistré !")

# --- AUTRES PAGES (Conservées) ---
elif st.session_state.page == "Production":
    st.title("🌱 Production")
    # Code production précédent...

elif st.session_state.page == "Météo":
    st.title("☁️ Météo")
    components.html('<iframe src="https://www.meteoblue.com/fr/meteo/widget/three/korhogo_c%c3%b4te-d%27ivoire_2286420?geoloc=fixed&days=4&tempunit=CELSIUS&layout=light" frameborder="0" style="width: 100%; height: 600px"></iframe>', height=620)

else:
    st.title("🚜 Accueil LUN-AGRO")
    st.info("Sélectionnez une option dans le menu à gauche.")
