import os
import sys
import urllib.parse
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

# 1. Configuration des chemins d'accès
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(DASHBOARD_DIR)

for path in [DASHBOARD_DIR, PROJECT_ROOT]:
  if path not in sys.path:
    sys.path.insert(0, path)

try:
  from components.map import render_map
except ImportError:
  from dashboard.components.map import render_map

# Import des listes de villes
try:
  from config.cities import (
      BAHRAIN_CITIES,
      KUWAIT_CITIES,
      MOROCCO_CITIES,
      QATAR_CITIES,
      SAUDI_ARABIA_CITIES,
      UAE_CITIES,
  )
except ImportError:
  MOROCCO_CITIES = ["Casablanca", "Rabat", "Marrakech", "Tangier", "Agadir"]
  SAUDI_ARABIA_CITIES = ["Riyadh", "Jeddah", "Mecca", "Medina", "Dammam"]
  UAE_CITIES = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman"]
  QATAR_CITIES = ["Doha", "Lusail", "Al Rayyan", "Al Wakrah"]
  KUWAIT_CITIES = ["Kuwait City", "Salmiya", "Hawalli", "Fahaheel"]
  BAHRAIN_CITIES = ["Manama", "Muharraq", "Riffa", "Seef"]

COUNTRY_CITIES_MAP = {
    "Morocco": {
        "cities": MOROCCO_CITIES,
        "aliases": ["morocco", "maroc", "ma"],
    },
    "Saudi Arabia": {
        "cities": SAUDI_ARABIA_CITIES,
        "aliases": ["saudi arabia", "arabie saoudite", "sa"],
    },
    "United Arab Emirates": {
        "cities": UAE_CITIES,
        "aliases": ["united arab emirates", "emirates", "uae", "émirats arabes unis"],
    },
    "Qatar": {"cities": QATAR_CITIES, "aliases": ["qatar", "qa"]},
    "Kuwait": {"cities": KUWAIT_CITIES, "aliases": ["kuwait", "koweit", "kw"]},
    "Bahrain": {"cities": BAHRAIN_CITIES, "aliases": ["bahrain", "bahreïn", "bh"]},
}

st.set_page_config(
    page_title="Carte Interactive", page_icon="🗺️", layout="wide"
)

# --- CHARGEMENT AUTOMATIQUE DE POSTGRESQL ---
load_dotenv()


@st.cache_resource
def get_db_engine():
  DB_USER = os.getenv("DB_USER", "postgres")
  DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
  DB_HOST = os.getenv("DB_HOST", "localhost")
  DB_PORT = os.getenv("DB_PORT", "5432")
  DB_NAME = os.getenv("DB_NAME", "restaurants_db")
  password_encoded = urllib.parse.quote_plus(DB_PASSWORD)
  url = f"postgresql://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
  return create_engine(url)


@st.cache_data(ttl=300)
def load_data(_engine):
  query = "SELECT * FROM restaurants;"
  return pd.read_sql(query, _engine)


def get_or_load_dataframe():
  """Récupère le DataFrame du session_state ou le recharge automatiquement."""
  if "df" in st.session_state and not st.session_state["df"].empty:
    return st.session_state["df"]

  try:
    engine = get_db_engine()
    df = load_data(engine)
    st.session_state["engine"] = engine
    st.session_state["df"] = df
    return df
  except Exception as e:
    st.error(f"Erreur de rechargement des données : {e}")
    return pd.DataFrame()


# --- TITRE ET BOUTON DE FORÇAGE ---
st.title("🗺️ Carte Interactive des Restaurants")

# Bouton de rafraîchissement forcé depuis la BDD
if st.button("🔄 Rafraîchir les données depuis PostgreSQL"):
  if "df" in st.session_state:
    del st.session_state["df"]  # Supprime l'ancien tableau en mémoire
  st.cache_data.clear()  # Vide le cache SQL
  st.rerun()  # Relance la page proprement

# Récupération sécurisée du DataFrame
df = get_or_load_dataframe()

if not df.empty:
  # Nettoyage et conversion explicite des coordonnées GPS
  df_clean = df.copy()
  if "latitude" in df_clean.columns:
    df_clean["latitude"] = pd.to_numeric(df_clean["latitude"], errors="coerce")
  if "longitude" in df_clean.columns:
    df_clean["longitude"] = pd.to_numeric(
        df_clean["longitude"], errors="coerce"
    )

  col_filters, col_map = st.columns([1, 3])

  with col_filters:
    st.subheader("🔍 Filtres de la carte")

    # 1. Filtre Pays
    available_countries = ["Tous"] + list(COUNTRY_CITIES_MAP.keys())
    selected_country = st.selectbox("Pays :", available_countries)

    # 2. Filtre Ville
    selected_city = "Toutes"
    if selected_country != "Tous":
      country_cities = COUNTRY_CITIES_MAP[selected_country]["cities"]
      selected_city = st.selectbox(
          f"Ville ({selected_country}) :",
          ["Toutes"] + sorted(country_cities),
      )

    # 3. Filtre Cuisine
    selected_cuisine = "Toutes"
    if "cuisine" in df_clean.columns:
      raw_cuisines = df_clean["cuisine"].dropna().unique().tolist()
      valid_cuisines = sorted([
          str(c).strip()
          for c in raw_cuisines
          if str(c).strip() and str(c).lower() not in ["not existed", "none"]
      ])
      selected_cuisine = st.selectbox(
          "Type de Cuisine :", ["Toutes"] + valid_cuisines
      )

    # 4. Note minimale
    min_rating = st.slider("Note minimale ⭐ :", 0.0, 5.0, 0.0, 0.1)

    # --- APPLICATION DES FILTRES ---
    filtered_df = df_clean.copy()

    if selected_country != "Tous" and "country" in filtered_df.columns:
      aliases = COUNTRY_CITIES_MAP[selected_country]["aliases"]
      filtered_df = filtered_df[
          filtered_df["country"]
          .astype(str)
          .str.strip()
          .str.lower()
          .isin(aliases)
      ]

    if selected_city != "Toutes" and "city" in filtered_df.columns:
      filtered_df = filtered_df[
          filtered_df["city"].astype(str).str.strip().str.lower()
          == selected_city.lower()
      ]

    if selected_cuisine != "Toutes" and "cuisine" in filtered_df.columns:
      filtered_df = filtered_df[filtered_df["cuisine"] == selected_cuisine]

    if "rating" in filtered_df.columns:
      filtered_df = filtered_df[filtered_df["rating"] >= min_rating]

    has_gps = (
        filtered_df["latitude"].notna() & filtered_df["longitude"].notna()
    )
    

  with col_map:
    render_map(filtered_df, max_markers=None)

else:
  st.error("❌ Impossible de se connecter à la base de données PostgreSQL.")