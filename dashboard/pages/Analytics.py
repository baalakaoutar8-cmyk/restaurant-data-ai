import os
import sys
import urllib.parse
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

# Ajout de la racine pour importer depuis dashboard.components et dashboard.charts
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)

from dashboard.charts.kpis import (
    chart_cuisine_distribution,
    chart_rating_distribution,
    chart_restaurants_by_city,
)
from dashboard.charts.reviews_chart import chart_reviews_distribution
from dashboard.components.kpi_cards import render_kpi_cards

# Dictionnaire de correspondance des noms de pays
COUNTRY_MAPPING = {
    "morocco": "Morocco",
    "maroc": "Morocco",
    "ma": "Morocco",
    "saudi arabia": "Saudi Arabia",
    "arabie saoudite": "Saudi Arabia",
    "ksa": "Saudi Arabia",
    "united arab emirates": "United Arab Emirates",
    "uae": "United Arab Emirates",
    "eau": "United Arab Emirates",
    "émirats arabes unis": "United Arab Emirates",
    "qatar": "Qatar",
    "kuwait": "Kuwait",
    "koweït": "Kuwait",
    "bahrain": "Bahrain",
    "bahreïn": "Bahrain",
}

ALLOWED_COUNTRIES = [
    "Morocco",
    "Saudi Arabia",
    "United Arab Emirates",
    "Qatar",
    "Kuwait",
    "Bahrain",
]

# Dictionnaire d'association Pays -> Devise
CURRENCY_MAP = {
    "Morocco": "MAD",
    "Saudi Arabia": "SAR",
    "United Arab Emirates": "AED",
    "Qatar": "QAR",
    "Kuwait": "KWD",
    "Bahrain": "BHD",
}

load_dotenv()

st.set_page_config(
    page_title="Dashboard Analytique", page_icon="📊", layout="wide"
)


# --- FONCTIONS DE CHARGEMENT & RAFRAÎCHISSEMENT ---
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
def load_data_from_db():
    engine = get_db_engine()
    query = "SELECT * FROM restaurants;"
    return pd.read_sql(query, engine)


def get_or_load_dataframe():
    if "df" in st.session_state and not st.session_state["df"].empty:
        return st.session_state["df"]

    try:
        df = load_data_from_db()
        st.session_state["df"] = df
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return pd.DataFrame()


# --- GRAPHIQUE PAYS ---
def chart_restaurants_by_country(data: pd.DataFrame):
    if "country" not in data.columns or data["country"].dropna().empty:
        return px.bar(title="Nombre de restaurants par pays (Aucune donnée)")

    df_copy = data.copy()

    df_copy["clean_country"] = (
        df_copy["country"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(COUNTRY_MAPPING)
    )

    filtered_data = df_copy[df_copy["clean_country"].isin(ALLOWED_COUNTRIES)]

    if filtered_data.empty:
        return px.bar(title="Nombre de restaurants par pays (Aucune donnée)")

    df_country = filtered_data["clean_country"].value_counts().reset_index()
    df_country.columns = ["country", "count"]

    fig = px.bar(
        df_country,
        x="count",
        y="country",
        orientation="h",
        title="Nombre de restaurants par pays",
        labels={"count": "Nombre de restaurants", "country": "Pays"},
        color="count",
        color_continuous_scale="Viridis",
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"}, showlegend=False, height=400
    )
    return fig


# --- ENTÊTE ET BOUTON DE RAFRAÎCHISSEMENT ---
col_title, col_btn = st.columns([4, 1])

with col_title:
    st.title("📊 Tableau de Bord Analytique")

with col_btn:
    st.write("")
    if st.button("🔄 Rafraîchir les données", use_container_width=True):
        if "df" in st.session_state:
            del st.session_state["df"]
        st.cache_data.clear()
        st.rerun()

# Récupération des données
df = get_or_load_dataframe()

if not df.empty:
    # Utilisation directe des données complètes sans la barre de filtres
    filtered_df = df

    # 1. Cartes KPIs
    render_kpi_cards(filtered_df)
    st.markdown("---")

    # 2. Graphiques : Répartition géographique
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            chart_restaurants_by_country(filtered_df), use_container_width=True
        )
    with c2:
        st.plotly_chart(
            chart_restaurants_by_city(filtered_df), use_container_width=True
        )

    st.markdown("---")

    # 3. Graphiques : Cuisine & Distribution des Notes
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(
            chart_cuisine_distribution(filtered_df), use_container_width=True
        )
    with c4:
        st.plotly_chart(
            chart_rating_distribution(filtered_df), use_container_width=True
        )

    st.markdown("---")

    # 4. Top Restaurants les plus évalués
    st.plotly_chart(
        chart_reviews_distribution(filtered_df), use_container_width=True
    )

    st.markdown("---")

    # 5. Classement des Meilleurs Restaurants
    st.subheader("🏆 Classement des Meilleurs Restaurants")

    # Définition des colonnes à extraire
    target_cols = [
        "name",
        "city",
        "country",
        "cuisine",
        "rating",
        "predicted_rating",
        "avg_price",
    ]

    available_cols = [c for c in target_cols if c in filtered_df.columns]

    # Tri par rating puis predicted_rating si disponible
    sort_cols = [c for c in ["rating", "predicted_rating"] if c in filtered_df.columns]
    ascending_flags = [False] * len(sort_cols)

    if sort_cols:
        top_df = (
            filtered_df[available_cols]
            .sort_values(by=sort_cols, ascending=ascending_flags)
            .head(10)
            .copy()
        )
    else:
        top_df = filtered_df[available_cols].head(10).copy()

    # Formatage automatique de Prix Moyen + Devise par pays
    if "avg_price" in top_df.columns:
        def format_price_with_currency(row):
            val = row["avg_price"]
            if pd.isna(val) or val == 0:
                return "N/A"

            country_raw = str(row.get("country", "")).strip().lower()
            normalized_country = COUNTRY_MAPPING.get(country_raw, row.get("country", ""))
            curr = CURRENCY_MAP.get(normalized_country, "")

            return f"{val:.2f} {curr}".strip()

        top_df["avg_price"] = top_df.apply(format_price_with_currency, axis=1)

    st.dataframe(top_df, use_container_width=True)

else:
    st.error(
        "⚠️ Aucune donnée n'a pu être chargée depuis la base de données PostgreSQL."
    )