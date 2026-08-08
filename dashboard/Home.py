import os
import sys
import urllib.parse
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

# Configuration du chemin racine
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Accueil | Plateforme Gastronomique Maroc",
    page_icon="⚜️",
    layout="wide",
)

# --- INJECTION CSS ---
st.markdown(
    """
<style>
/* 1. Image de fond : Transparence fixe à 0.15 en haut et en bas */
[data-testid="stAppViewContainer"] {
    background-image: linear-gradient(rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.15)), 
                      url("https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1920&auto=format&fit=crop") !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}

/* Transparence des blocs internes */
[data-testid="stHeader"], .main, .block-container {
    background: transparent !important;
}

/* 2. SIDEBAR (MENU LATÉRAL) : Couleur rgb(234, 222, 164) */
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {
    background-color: rgb(234, 222, 164) !important;
    border-right: 1px solid #CBB265 !important;
}

/* Textes de la Sidebar */
[data-testid="stSidebar"] * {
    color: #1A1A1A !important;
    font-weight: 600 !important;
}

/* Mise en valeur de l'onglet actif dans le menu */
[data-testid="stSidebar"] [aria-selected="true"] {
    background-color: rgba(255, 255, 255, 0.6) !important;
    font-weight: bold !important;
}

/* 3. EN-TÊTE CENTRÉE & BANDEAU DE LISIBILITÉ */
.header-container {
    text-align: center !important;
    padding: 22px 30px;
    margin-bottom: 25px;
    background: rgba(255, 255, 255, 0.25) !important;
    backdrop-filter: blur(8px);
    border-radius: 20px;
    border: 1px solid rgba(203, 178, 101, 0.4) !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
}

.gold-title {
    color: #654D0F !important;
    font-weight: 900 !important;
    font-family: 'Cinzel', 'Playfair Display', serif, sans-serif;
    font-size: 2.8rem !important;
    margin-bottom: 8px !important;
    text-align: center !important;
}

.gold-subtitle {
    color: #111111 !important;
    font-style: italic;
    font-weight: 600 !important;
    font-size: 1.15rem !important;
    letter-spacing: 0.5px;
    margin: 0 !important;
    text-align: center !important;
}

/* 4. BOÎTES KPI */
.metric-box {
    background: #FFFFFF !important;
    border-left: 4px solid #CBB265 !important;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.12);
}

.metric-val {
    color: #000000 !important;
    font-size: 1.8rem;
    font-weight: 900;
    margin: 0;
}

.metric-lbl {
    color: #333333 !important;
    font-size: 0.85rem;
    margin: 4px 0 0 0;
    text-transform: uppercase;
    font-weight: 700;
}

/* 5. CARTES DE FONCTIONNALITÉS */
.feature-card {
    background: #FFFFFF !important;
    border: 1px solid #E5E0CB !important;
    border-top: 3px solid #CBB265 !important;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    min-height: 175px;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.feature-card:hover {
    border-color: #CBB265 !important;
    transform: translateY(-4px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.30);
}

.feature-icon {
    font-size: 2rem;
    margin-bottom: 10px;
}

.feature-title {
    color: #000000 !important;
    font-size: 1.2rem;
    font-weight: 800;
    margin-bottom: 8px;
}

.feature-desc {
    color: #222222 !important;
    font-size: 0.93rem;
    line-height: 1.5;
    font-weight: 500;
    margin: 0;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)


# --- FONCTIONS ANTI-RAFRAÎCHISSEMENT (`F5`) ---
@st.cache_resource
def init_db_engine():
    """Conserve le moteur SQLAlchemy en cache global."""
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "restaurants_db")

    password_encoded = urllib.parse.quote_plus(DB_PASSWORD)
    url = f"postgresql://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)


@st.cache_data(ttl=300)
def load_data_from_db():
    """Conserve le DataFrame principal en cache global."""
    engine = init_db_engine()
    return pd.read_sql("SELECT * FROM restaurants;", engine)


# Synchronisation session_state
if "engine" not in st.session_state or st.session_state["engine"] is None:
    try:
        st.session_state["engine"] = init_db_engine()
    except Exception as e:
        st.error(f"❌ Erreur de connexion à la base de données : {e}")

if "df" not in st.session_state or st.session_state["df"].empty:
    try:
        st.session_state["df"] = load_data_from_db()
    except Exception as e:
        st.session_state["df"] = pd.DataFrame()

df = st.session_state.get("df", pd.DataFrame())

# --- EN-TÊTE CENTRÉ AVEC CARTE DÉPOLIE ---
st.markdown(
    """
    <div class="header-container">
        <h1 class="gold-title">⚜️ Portail Gastronomique du Maroc</h1>
        <p class="gold-subtitle">L'Excellence Analytique & l'Intelligence Artificielle au Service de la Haute Gastronomie</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- APERÇU RAPIDE DES CHIFFRES (KPIS CLAIRS) ---
if not df.empty:
    m1, m2, m3, m4 = st.columns(4)

    villes_count = f"{df['city'].nunique():,}" if "city" in df.columns else "N/A"
    cuisines_count = (
        f"{df['cuisine'].nunique():,}" if "cuisine" in df.columns else "N/A"
    )
    note_moy = (
        f"⭐ {df['rating'].mean():.2f}"
        if "rating" in df.columns and not df["rating"].isna().all()
        else "N/A"
    )

    with m1:
        st.markdown(
            f'<div class="metric-box"><div class="metric-val">{len(df):,}</div><div class="metric-lbl">Établissements</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="metric-box"><div class="metric-val">{villes_count}</div><div class="metric-lbl">Villes Couvertes</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="metric-box"><div class="metric-val">{cuisines_count}</div><div class="metric-lbl">Types de Cuisine</div></div>',
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f'<div class="metric-box"><div class="metric-val">{note_moy}</div><div class="metric-lbl">Note Moyenne</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# --- GRILLE DES MODULES DE NAVIGATION ---
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
<div class="feature-card">
    <div class="feature-icon">📊</div>
    <div class="feature-title">Statistiques & Analytics</div>
    <div class="feature-desc">
        Explorez la répartition géographique des établissements, l'analyse comparative des notes, la densité des cuisines et le classement exclusif du Top 10.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="feature-card">
    <div class="feature-icon">🤖</div>
    <div class="feature-title">Recommandations Machine Learning</div>
    <div class="feature-desc">
        Profitez d'un algorithme de scoring prédictif pour découvrir les restaurants à fort potentiel et anticiper la satisfaction culinaire.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
<div class="feature-card">
    <div class="feature-icon">👑</div>
    <div class="feature-title">Concierge IA Gastronomique</div>
    <div class="feature-desc">
        Interrogez notre registre en langage naturel via Text-to-SQL / RAG pour obtenir des conseils personnalisés et sur-mesure instantanément.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="feature-card">
    <div class="feature-icon">🗺️</div>
    <div class="feature-title">Cartographie Interactive</div>
    <div class="feature-desc">
        Localisez avec précision les meilleures adresses sur une carte interactive et parcourez le répertoire complet des tables du Maroc.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )