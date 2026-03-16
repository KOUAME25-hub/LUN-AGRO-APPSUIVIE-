import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import streamlit.components.v1 as components

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

# Base de données stable
DB_NAME = "lun_agro_v2026_final.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS production 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, 
                  provenance TEXT, superficie TEXT, lieu TEXT, qte_rec REAL, dechets REAL, 
                  qte_livrable REAL, montant REAL, mode_paiement TEXT, moyen_paiement TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS phyto 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, produit TEXT, cible TEXT, 
                  parcelle TEXT, dose TEXT, applicateur TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS agenda 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, tache TEXT, responsable TEXT, statut TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS formation 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, theme TEXT, formateur TEXT, participants TEXT, duree TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- MENU LATÉRAL (ICÔNES) ---
st.sidebar.title("🍀 LUN-AGRO PRO")
st.sidebar.write("---")

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# Navigation
menu_items = {
    "🏠 Accueil": "Accueil",
    "📅 Agenda": "Agenda",
    "🌱 Production": "Production",
    "🧪 Phyto": "Phyto",
    "💰 Finances": "Finances",
    "📚 Formation": "Formation",
    "☁️ Météo": "Météo"
}

for label, page in menu_items.items():
    if st.sidebar.button(label, use_container_width=True):
        st.session_state.page = page

# --- LOGIQUE DES PAGES ---

# 1. FORMATION & ATTESTATION
if st.session_state.page == "Formation":
    st.title("📚 Formations & Certifications")
    
    with st.form("f_formation"):
        c1, c2 = st.columns(2)
        theme = c1.text_input("Thème de la formation")
        formateur = c2.text_input("Formateur")
        part = c1.text_area("Participants (un nom par ligne)")
        duree = c2.text_input("Durée")
        d_f = st.date_input("Date")
        if st.form_submit_button("Enregistrer"):
            conn.execute("INSERT INTO formation (date, theme, formateur, participants, duree) VALUES (?,?,?,?,?)",
                         (d_f.strftime("%d/%m/%Y"), theme, formateur, part, duree))
            conn.commit()
            st.success("Formation enregistrée !")

    st.write("---")
    st.subheader("🎓 Générer une Attestation")
    df_f = pd.read_sql_query("SELECT * FROM formation ORDER BY id DESC", conn)
    
    if not df_f.empty:
        selected_f = st.selectbox("Choisir une formation réalisée", df_f['theme'].unique())
        nom_eleve = st.text_input("Nom de l'employé à certifier")
        
        if st.button("Générer le visuel de l'attestation"):
            f_data = df_f[df_f['theme'] == selected_f].iloc[0]
            st.markdown(f"""
            <div style="border: 10px solid #2E7D32; padding: 50px; text-align: center; background-color: white; color: black; font-family: serif;">
                <h1 style="color: #2E7D32;">ATTESTATION DE FORMATION</h1>
                <p style="font-size: 20px;">LUN-AGRO PRO - Korhogo, Côte d'Ivoire</p>
                <hr style="width: 50%; border: 1px solid #2E7D32;">
                <p style="font-size: 24px;">Il est certifié que</p>
                <h2 style="text-transform: uppercase;">{nom_eleve}</h2>
                <p style="font-size: 20px;">a suivi avec succès la formation technique sur le thème :</p>
                <h3>{selected_f}</h3>
                <p style="font-size: 18px;">Réalisée le {f_data['date']} | Durée : {f_data['duree']}</p>
                <br><br>
                <div style="display: flex; justify-content: space-around;">
                    <p>Le Formateur :<br><b>{f_data['formateur']}</b></p>
                    <p>La Direction :<br><b>LUN-AGRO</b></p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.write("### 📖 Historique")
    st.dataframe(df_f, use_container_width=True)

# 2. PRODUCTION (COMPLET)
elif st.session_state.page == "Production":
    st.title("🌱 Production")
    t1, t2, t3 = st.tabs(["🆕 Semer", "🧺 Récolter", "💵 Vendre"])
    with t1:
        with st.form("f1"):
            c1, c2 = st.columns(2)
            p_s = c1.text_input("Produit Semis")
            prov = c2.text_input("Provenance")
            sup = c1.text_input("Superficie")
            lieu = c2.text_input("Parcelle/Abris")
            if st.form_submit_button("Enregistrer Semis"):
                conn.execute("INSERT INTO production (date, type, produit, provenance, superficie, lieu) VALUES (?,?,?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Semis", p_s, prov, sup, lieu))
                conn.commit(); st.rerun()
    with t2:
        with st.form("f2"):
            p_r = st.text_input("Produit Récolté")
            q_r = st.number_input("Quantité", min_value=0.0)
            d = st.number_input("Déchets", min_value=0.0)
            if st.form_submit_button("Enregistrer Récolte"):
                conn.execute("INSERT INTO production (date, type, produit, qte_rec, dechets, qte_livrable) VALUES (?,?,?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Récolte", p_r, q_r, d, q_r-d))
                conn.commit(); st.rerun()
    with t3:
        with st.form("f3"):
            p_v = st.text_input("Produit Vendu")
            m = st.number_input("Montant (FCFA)", min_value=0.0)
            mod = st.selectbox("Mode", ["Cash", "Crédit"])
            if st.form_submit_button("Enregistrer Vente"):
                conn.execute("INSERT INTO production (date, type, produit, montant, mode_paiement) VALUES (?,?,?,?,?)",
                             (date.today().strftime("%d/%m/%Y"), "Vente", p_v, m, mod))
                conn.commit(); st.rerun()
    st.dataframe(pd.read_sql_query("SELECT * FROM production ORDER BY id DESC", conn))

# 3. PHYTO
elif st.session_state.page == "Phyto":
    st.title("🧪 Phyto")
    with st.form("f_p"):
        p = st.text_input("Produit"); c = st.text_input("Cible"); l = st.text_input("Parcelle"); d = st.text_input("Dose")
        if st.form_submit_button("Valider"):
            conn.execute("INSERT INTO phyto (date, produit, cible, parcelle, dose) VALUES (?,?,?,?,?)",
                         (date.today().strftime("%d/%m/%Y"), p, c, l, d)); conn.commit(); st.rerun()
    st.dataframe(pd.read_sql_query("SELECT * FROM phyto ORDER BY id DESC", conn))

# 4. FINANCES
elif st.session_state.page == "Finances":
    st.title("💰 Finances")
    val = pd.read_sql_query("SELECT SUM(montant) FROM production WHERE type='Vente'", conn).iloc[0,0] or 0
    st.metric("Total des Ventes", f"{val} FCFA")
    st.table(pd.read_sql_query("SELECT date, produit, montant, mode_paiement FROM production WHERE type='Vente'", conn))

# 5. MÉTÉO
elif st.session_state.page == "Météo":
    st.title("☁️ Météo Korhogo")
    components.html('<iframe src="https://www.meteoblue.com/fr/meteo/widget/three/korhogo_c%c3%b4te-d%27ivoire_2286420?geoloc=fixed&days=4&tempunit=CELSIUS&layout=light" frameborder="0" style="width: 100%; height: 600px"></iframe>', height=620)

else:
    st.title("🚜 Accueil LUN-AGRO")
    st.info("Sélectionnez une icône à gauche pour commencer.")
