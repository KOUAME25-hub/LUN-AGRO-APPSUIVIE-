import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import date

# --- CONFIGURATION ---
st.set_page_config(page_title="LUN-AGRO PRO", layout="wide")

# Fonction pour crypter les mots de passe (plus sécurisé)
def crypter(mdp):
    return hashlib.sha256(str.encode(mdp)).hexdigest()

# --- BASE DE DONNÉES ---
conn = sqlite3.connect('ferme_v6.db', check_same_thread=False)
c = conn.cursor()
# Table des utilisateurs (Admin par défaut créé au lancement)
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
# Création du compte Admin principal s'il n'existe pas
admin_pwd = crypter("agri2026")
c.execute('INSERT OR IGNORE INTO users VALUES (?,?,?)', ("admin", admin_pwd, "Administrateur"))
# Table RH
c.execute('CREATE TABLE IF NOT EXISTS rh (date TEXT, nom TEXT, poste TEXT, salaire REAL)')
conn.commit()

# --- SYSTEME DE CONNEXION ---
if "connecte" not in st.session_state:
    st.session_state.connecte = False
    st.session_state.user_role = None

if not st.session_state.connecte:
    st.title("🔐 Connexion LUN-AGRO")
    user_input = st.text_input("Identifiant")
    pw_input = st.text_input("Mot de passe", type="password")
    
    if st.button("SE CONNECTER"):
        c.execute('SELECT password, role FROM users WHERE username = ?', (user_input,))
        resultat = c.fetchone()
        if resultat and resultat[0] == crypter(pw_input):
            st.session_state.connecte = True
            st.session_state.username = user_input
            st.session_state.user_role = resultat[1]
            st.rerun()
        else:
            st.error("Identifiants incorrects")
    st.stop()

# --- INTERFACE APRES CONNEXION ---

# Style des boutons
st.markdown("""<style> div.stButton > button { height: 80px; border-radius: 12px; } </style>""", unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page = "🏠 Accueil"

# Barre de navigation (Menu par icônes)
col1, col2, col3, col4, col5 = st.columns(5)
with col1: 
    if st.button("🏠\nAccueil"): st.session_state.page = "Accueil"
with col2: 
    if st.button("🌱\nProduction"): st.session_state.page = "Production"
with col3: 
    if st.button("💰\nFinances"): st.session_state.page = "Finances"
with col4: 
    if st.button("👥\nRH"): st.session_state.page = "RH"
with col5: 
    if st.button("⚙️\nRéglages"): st.session_state.page = "Réglages"

st.divider()

# --- GESTION DES PAGES ---

if st.session_state.page == "RH":
    st.subheader("👥 Gestion RH")
    # Formulaire RH classique...
    with st.form("rh_form"):
        nom = st.text_input("Nom de l'ouvrier")
        paie = st.number_input("Salaire", min_value=0)
        if st.form_submit_button("Enregistrer"):
            c.execute("INSERT INTO rh VALUES (?,?,?,?)", (date.today(), nom, "Ouvrier", paie))
            conn.commit()
            st.success("Enregistré")

elif st.session_state.page == "Réglages":
    st.subheader("⚙️ Paramètres du système")
    
    # --- SECTION RÉSERVÉE À L'ADMINISTRATEUR ---
    if st.session_state.user_role == "Administrateur":
        st.write("---")
        st.markdown("### 👤 Créer un nouveau compte utilisateur")
        st.info("En tant qu'Admin, vous seul voyez cette section.")
        
        with st.form("creer_compte"):
            new_user = st.text_input("Nouvel Identifiant")
            new_pw = st.text_input("Mot de passe", type="password")
            new_role = st.selectbox("Niveau d'accès", ["Utilisateur", "Administrateur"])
            
            if st.form_submit_button("CRÉER LE COMPTE"):
                if new_user and new_pw:
                    try:
                        c.execute('INSERT INTO users VALUES (?,?,?)', (new_user, crypter(new_pw), new_role))
                        conn.commit()
                        st.success(f"Compte créé pour {new_user} !")
                    except:
                        st.error("Cet identifiant existe déjà.")
                else:
                    st.warning("Veuillez remplir tous les champs.")
    else:
        st.warning("Accès restreint : Seul l'Administrateur peut créer des comptes.")

    if st.button("Se déconnecter"):
        st.session_state.connecte = False
        st.rerun()
