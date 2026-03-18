import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import date
from io import BytesIO
from fpdf import FPDF # Importation pour le PDF

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

def crypter(mdp):
    return hashlib.sha256(str.encode(mdp)).hexdigest()

# --- FONCTION GÉNÉRATION PDF ---
def generer_pdf_fiche(nom, mois, montant, date_p):
    pdf = FPDF()
    pdf.add_page()
    
    # En-tête
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "LUN-AGRO PRO - KORHOGO", ln=True, align="C")
    pdf.set_font("Arial", "I", 10)
    pdf.cell(200, 10, "Bulletin de Paie Officiel", ln=True, align="C")
    pdf.ln(10)
    
    # Contenu
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Date d'émission : {date.today().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, f"Nom de l'employé : {nom}", ln=True)
    pdf.cell(200, 10, f"Période : Mois de {mois}", ln=True)
    pdf.cell(200, 10, f"Montant versé : {montant} FCFA", ln=True)
    pdf.cell(200, 10, f"Date du paiement : {date_p}", ln=True)
    
    pdf.ln(20)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(200, 10, "Signature de l'employeur (LUN-AGRO)", ln=True, align="R")
    
    return pdf.output()

# --- CONNEXION ET CRÉATION ---
DB_PATH = "data_ferme_permanente.db"

def initialiser_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS rh_personnel 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, poste TEXT, contact TEXT, salaire_base REAL, date_embauche TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS rh_paie 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, mois TEXT, montant_verse REAL, date_paiement TEXT)''')
    c.execute('CREATE TABLE IF NOT EXISTS production (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, produit TEXT, superficie TEXT, montant REAL)')
    
    c.execute('SELECT COUNT(*) FROM users WHERE username = "admin"')
    if c.fetchone()[0] == 0:
        admin_pwd = crypter("agri2026")
        c.execute('INSERT INTO users VALUES (?,?,?)', ("admin", admin_pwd, "Administrateur"))
    conn.commit()
    return conn

conn = initialiser_db()
cursor = conn.cursor()

# --- SYSTÈME DE CONNEXION ---
if "connecte" not in st.session_state: st.session_state.connecte = False
if not st.session_state.connecte:
    st.title("🔐 Connexion LUN-AGRO")
    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")
    if st.button("SE CONNECTER"):
        cursor.execute('SELECT password, role FROM users WHERE username = ?', (u,))
        res = cursor.fetchone()
        if res and res[0] == crypter(p):
            st.session_state.connecte, st.session_state.user_role, st.session_state.username = True, res[1], u
            st.rerun()
    st.stop()

# --- MENU NAVIGATION ---
if "page" not in st.session_state: st.session_state.page = "Accueil"
n_cols = 5 if st.session_state.user_role == "Administrateur" else 3
cols = st.columns(n_cols)

with cols[0]:
    if st.button("🏠\nAccueil", use_container_width=True): st.session_state.page = "Accueil"
with cols[1]:
    if st.button("🌱\nProduction", use_container_width=True): st.session_state.page = "Production"
with cols[2]:
    if st.button("💰\nFinances", use_container_width=True): st.session_state.page = "Finances"
if st.session_state.user_role == "Administrateur":
    with cols[3]:
        if st.button("👥\nRH", use_container_width=True): st.session_state.page = "RH"
    with cols[4]:
        if st.button("⚙️\nRéglages", use_container_width=True): st.session_state.page = "Réglages"

st.divider()

# --- LOGIQUE RH ---
if st.session_state.page == "RH" and st.session_state.user_role == "Administrateur":
    st.title("👥 Gestion des Ressources Humaines")
    tab_perso, tab_paie, tab_list = st.tabs(["➕ Ajouter Personnel", "💸 Effectuer un Paiement", "📋 Registre & Fiches PDF"])
    
    with tab_perso:
        with st.form("form_rh"):
            st.subheader("Fiche de nouvel employé")
            col1, col2 = st.columns(2)
            nom = col1.text_input("Nom Complet")
            poste = col2.selectbox("Poste", ["Ouvrier Agricole", "Chef de Culture", "Gardien", "Chauffeur", "Stagiaire"])
            contact = col1.text_input("Téléphone")
            salaire = col2.number_input("Salaire de Base (FCFA)", min_value=0)
            if st.form_submit_button("Enregistrer l'employé"):
                cursor.execute("INSERT INTO rh_personnel (nom, poste, contact, salaire_base, date_embauche) VALUES (?,?,?,?,?)",
                             (nom, poste, contact, salaire, date.today().strftime("%d/%m/%Y")))
                conn.commit(); st.success(f"Employé {nom} ajouté.")

    with tab_paie:
        st.subheader("Enregistrement des salaires")
        df_empl = pd.read_sql_query("SELECT nom FROM rh_personnel", conn)
        if not df_empl.empty:
            with st.form("form_paie"):
                emp_nom = st.selectbox("Sélectionner l'employé", df_empl['nom'])
                mois = st.selectbox("Mois de paie", ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])
                montant = st.number_input("Montant versé (FCFA)", min_value=0)
                if st.form_submit_button("Confirmer le paiement"):
                    cursor.execute("INSERT INTO rh_paie (nom, mois, montant_verse, date_paiement) VALUES (?,?,?,?)",
                                 (emp_nom, mois, montant, date.today().strftime("%d/%m/%Y")))
                    conn.commit(); st.success(f"Paiement enregistré.")
        else:
            st.warning("Veuillez d'abord ajouter du personnel.")

    with tab_list:
        st.subheader("Historique des paiements & Fiches PDF")
        df_hist = pd.read_sql_query("SELECT * FROM rh_paie ORDER BY id DESC", conn)
        
        if not df_hist.empty:
            for i, row in df_hist.iterrows():
                col_info, col_btn = st.columns([3, 1])
                col_info.write(f"📄 {row['nom']} - {row['mois']} ({row['montant_verse']} FCFA)")
                
                # Génération du PDF pour chaque ligne
                pdf_data = generer_pdf_fiche(row['nom'], row['mois'], row['montant_verse'], row['date_paiement'])
                col_btn.download_button(
                    label="📥 PDF",
                    data=bytes(pdf_data),
                    file_name=f"Fiche_Paie_{row['nom']}_{row['mois']}.pdf",
                    mime="application/pdf",
                    key=f"pdf_{row['id']}"
                )
        else:
            st.info("Aucun paiement enregistré pour le moment.")

# --- PAGES ACCUEIL & RÉGLAGES ---
elif st.session_state.page == "Réglages":
    st.subheader("⚙️ Gestion des Comptes")
    df_users = pd.read_sql_query("SELECT username, role FROM users", conn)
    st.dataframe(df_users)

elif st.session_state.page == "Accueil":
    st.info(f"Session active : {st.session_state.username} | Korhogo")
    st.metric("Total Employés", len(pd.read_sql_query("SELECT id FROM rh_personnel", conn)))

if st.sidebar.button("Déconnexion"):
    st.session_state.connecte = False
    st.rerun()
