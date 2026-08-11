import os
import sys
import urllib.parse
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Import direct du pipeline RAG (comme le fait chatbot.py)
from llm.rag import run_rag_pipeline

load_dotenv()

# Configuration du chemin racine du projet
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- INITIALISATION BDD (Identique à chatbot.py) ---
@st.cache_resource
def get_db_engine():
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "restaurants_db")

    password_encoded = urllib.parse.quote_plus(DB_PASSWORD)
    DATABASE_URL = f"postgresql://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(DATABASE_URL)

engine = get_db_engine()

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Concierge IA | Gastronomie",
    page_icon="👑",
    layout="wide"
)

# --- INITIALISATION DE L'HISTORIQUE DE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- STYLES CSS : TEXTES AGRANDIS & BARRE DE CHAT REHAUSSÉE ---
st.markdown("""
<style>
/* 1. Arrière-plan global clair */
[data-testid="stAppViewContainer"] {
    background-color: #FAF9F6 !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* 2. Sidebar claire */
[data-testid="stSidebar"] {
    background-color: #F7F5EC !important;
    border-right: 1px solid #E7E1C5 !important;
}

/* 3. Titre Principal - Agrandit (3.0rem) */
.gold-title {
    color: #8C6B1B !important;
    font-weight: 800 !important;
    font-family: 'Cinzel', 'Playfair Display', serif, sans-serif;
    font-size: 3rem !important;
    margin-bottom: 8px;
}

/* 4. Sous-titre - Agrandit (1.3rem) */
.gold-subtitle {
    color: #5C4713 !important;
    font-style: italic !important;
    font-weight: 500 !important;
    font-size: 1.3rem !important;
    margin-bottom: 2rem;
}

/* 5. Carte du Concierge - Textes plus grands */
.banner-box {
    background-color: #F7F5EC !important;
    border: 1px solid #E7E1C5 !important;
    border-left: 5px solid #8C6B1B !important;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 30px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.banner-title {
    color: #1A1A1A !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    margin-bottom: 8px;
}

.banner-desc {
    color: #333333 !important;
    font-size: 1.15rem !important;
    line-height: 1.6;
    margin: 0;
}

/* 6. Titre Suggestions - Agrandit */
.suggestions-label {
    color: #1A1A1A !important;
    font-weight: 700 !important;
    font-size: 1.25rem !important;
    margin-bottom: 16px;
}

/* 7. Boutons de Suggestions - Textes et rembourrage agrandis */
.stButton > button {
    background-color: #F7F5EC !important;
    color: #2D2D2E !important;
    border: 1.5px solid #CBB265 !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    padding: 10px 18px !important;
    transition: all 0.25s ease !important;
    width: 100%;
}

.stButton > button:hover {
    background-color: #8C6B1B !important;
    color: #FFFFFF !important;
    border-color: #8C6B1B !important;
}

/* 8. Barre de Saisie Chat (remontée plus haut + zone agrandie) */
[data-testid="stChatInput"] {
    background-color: #FFFFFF !important;
    border: 2px solid #CBB265 !important;
    border-radius: 16px !important;
    bottom: 50px !important;
    padding: 8px !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08) !important;
}

[data-testid="stChatInput"] textarea {
    color: #1A1A1A !important;
    font-size: 1.2rem !important;
    line-height: 1.5 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #666666 !important;
    font-size: 1.15rem !important;
}
</style>
""", unsafe_allow_html=True)

# --- INTERFACE UTILISATEUR ---

# En-tête
st.markdown('<h1 class="gold-title">⚜️ Concierge IA & Haute Gastronomie</h1>', unsafe_allow_html=True)
st.markdown('<p class="gold-subtitle">Votre Sommelier virtuel dédié à l\'exploration des meilleures tables et expériences culinaires.</p>', unsafe_allow_html=True)

# Carte de bienvenue
st.markdown("""
<div class="banner-box">
    <div class="banner-title">✨ Bienvenue dans votre service de Conciergerie sur-mesure</div>
    <div class="banner-desc">
        Interrogez notre registre en langage naturel pour obtenir des recommandations d'exception, sélectionner les tables les mieux notées ou explorer notre univers gastronomique.
    </div>
</div>
""", unsafe_allow_html=True)

# Suggestions de recherche
st.markdown('<div class="suggestions-label">💡 Suggestions de recherche :</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
prompt_selected = None

with col1:
    if st.button("🍷 Top 5 des tables étoilées à Casablanca", key="sug1"):
        prompt_selected = "Top 5 des tables étoilées à Casablanca"

with col2:
    if st.button("🍣 Meilleure cuisine Japonaise", key="sug2"):
        prompt_selected = "Meilleure cuisine Japonaise"

with col3:
    if st.button("⭐ Restaurants avec note maximale", key="sug3"):
        prompt_selected = "Restaurants avec note maximale"

st.markdown("<br>", unsafe_allow_html=True)

# Zone de chat
prompt_input = st.chat_input("💭 Demandez conseil à votre Concierge (ex: Quel est le meilleur restaurant italien à Casablanca ?)")

active_prompt = prompt_selected or prompt_input

# --- AFFICHAGE DE L'HISTORIQUE DE CONVERSATION ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**Vous :** {msg['content']}")
    else:
        st.markdown(f"**⚜️ Concierge :**\n\n{msg['content']}")

# --- EXÉCUTION DE LA REQUÊTE ---
if active_prompt:
    # 1. Sauvegarder et afficher la question de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": active_prompt})
    st.markdown(f"**Vous :** {active_prompt}")

    # 2. Exécuter le pipeline RAG directement
    with st.spinner("⚜️ Le Concierge consulte la base de données..."):
        try:
            response = run_rag_pipeline(active_prompt, engine)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.markdown(f"**⚜️ Concierge :**\n\n{response}")
        except Exception as e:
            st.error(f"❌ Erreur lors de la réponse du Concierge : {e}")