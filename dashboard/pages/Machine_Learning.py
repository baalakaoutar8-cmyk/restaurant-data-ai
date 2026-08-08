import os
import sys
import urllib.parse
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine

# Configuration des chemins d'accès
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(DASHBOARD_DIR)

for path in [DASHBOARD_DIR, PROJECT_ROOT]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Importation des listes de villes depuis config/cities.py
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
    MOROCCO_CITIES = ["Casablanca", "Rabat", "Marrakech"]
    SAUDI_ARABIA_CITIES = ["Riyadh", "Jeddah"]
    UAE_CITIES = ["Dubai", "Abu Dhabi"]
    QATAR_CITIES = ["Doha"]
    KUWAIT_CITIES = ["Kuwait City"]
    BAHRAIN_CITIES = ["Manama"]

# Dictionnaire associant les Pays à leurs Villes respectives
COUNTRIES_CITIES = {
    "Morocco": MOROCCO_CITIES,
    "Saudi Arabia": SAUDI_ARABIA_CITIES,
    "United Arab Emirates": UAE_CITIES,
    "Qatar": QATAR_CITIES,
    "Kuwait": KUWAIT_CITIES,
    "Bahrain": BAHRAIN_CITIES,
}

# Mappage automatique des devises par défaut par pays
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
    page_title="Machine Learning", page_icon="🤖", layout="wide"
)

# --- INJECTION CSS CORRIGÉE (RÉTABLISSEMENT DU SLIDER) ---
st.markdown("""
<style>
/* 1. Arrière-plan clair et propre */
[data-testid="stAppViewContainer"] {
    background-color: #FAF9F6 !important;
}

/* 2. Titres principaux en Noir Profond & Bronze Foncé */
h1 {
    color: #1A1A1A !important;
    font-weight: 800 !important;
    font-size: 2.5rem !important;
}

h2, h3, [data-testid="stHeader"] {
    color: #8C6B1B !important; /* Doré Foncé / Bronze */
    font-weight: 700 !important;
}

/* 3. Textes généraux et labels en Noir/Gris Sombre bien lisible */
p, label, .stMarkdown, div {
    color: #2D2D2E !important;
}

/* 4. Onglets (Tabs) : Textes bien nets et dorés sombres */
button[data-baseweb="tab"] {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    color: #4A4A4A !important;
    padding: 10px 20px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #8C6B1B !important;
    border-bottom-color: #8C6B1B !important;
    border-bottom-width: 3px !important;
    font-weight: 800 !important;
}

/* 5. CIBLAGE PRÉCIS DU SLIDER (Sans déformer le composant) */
div[data-baseweb="slider"] div[role="slider"] {
    background-color: #8C6B1B !important;
    border-color: #8C6B1B !important;
}

/* 6. Boutons de rafraîchissement et actions */
.stButton > button {
    background-color: #F7F5EC !important;
    color: #1A1A1A !important;
    border: 1.5px solid #8C6B1B !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    transition: all 0.25s ease !important;
}

.stButton > button:hover {
    background-color: #8C6B1B !important;
    color: #FFFFFF !important;
}

/* 7. Boîtes de sélection (Selectbox) */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1.5px solid #CBB265 !important;
    border-radius: 8px !important;
    color: #1A1A1A !important;
}
</style>
""", unsafe_allow_html=True)


# --- FONCTIONS DE GESTION DE LA BASE DE DONNÉES ET DU CACHE ---
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
    """Récupère le DataFrame de la session ou le recharge automatiquement depuis PostgreSQL."""
    if "df" in st.session_state and not st.session_state["df"].empty:
        return st.session_state["df"]

    try:
        engine = get_db_engine()
        df = load_data(engine)
        st.session_state["engine"] = engine
        st.session_state["df"] = df
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return pd.DataFrame()


# --- ALGORITHME DE RECOMMANDATION PAR PRÉFÉRENCES UTILISATEUR ---
def recommend_restaurants(
    df: pd.DataFrame,
    city: str = None,
    country: str = None,
    cuisine: str = None,
    max_price: float = None,
    top_n: int = 5,
) -> pd.DataFrame:
    """Recommande les meilleurs restaurants selon les préférences utilisateur."""
    if df.empty:
        return pd.DataFrame()

    filtered = df.copy()

    # 1. Filtre par Pays
    if country and country != "Tous" and "country" in filtered.columns:
        filtered = filtered[
            filtered["country"].astype(str).str.lower() == country.lower()
        ]

    # 2. Filtre par Ville
    if city and city != "Toutes" and "city" in filtered.columns:
        filtered = filtered[
            filtered["city"].astype(str).str.lower() == city.lower()
        ]

    # 3. Filtre par Cuisine
    if cuisine and cuisine != "Toutes" and "cuisine" in filtered.columns:
        filtered = filtered[
            filtered["cuisine"]
            .astype(str)
            .str.lower()
            .str.contains(cuisine.lower(), na=False)
        ]

    # 4. Filtre par Prix
    price_col = (
        "avg_price"
        if "avg_price" in filtered.columns
        else ("price_numeric" if "price_numeric" in filtered.columns else None)
    )
    if max_price is not None and price_col and price_col in filtered.columns:
        filtered = filtered[filtered[price_col] <= max_price]

    if filtered.empty:
        return pd.DataFrame()

    # Sélection de la colonne de note réelle ou finale
    rating_col = (
        "final_rating"
        if "final_rating" in filtered.columns
        else ("rating" if "rating" in filtered.columns else "predicted_rating")
    )

    if rating_col not in filtered.columns:
        filtered[rating_col] = 0.0

    if "reviews_count" not in filtered.columns:
        filtered["reviews_count"] = 0

    if "is_rating_estimated" not in filtered.columns:
        filtered["is_rating_estimated"] = False

    # Score de recommandation interne pour trier
    reviews_log = np.log1p(filtered["reviews_count"].fillna(0))
    filtered["recommendation_score"] = (
        filtered[rating_col].fillna(0) * (reviews_log + 1)
    ).round(2)

    # Tri des résultats
    sort_cols = ["is_rating_estimated", "recommendation_score", rating_col]
    ascending_rules = [True, False, False]
    results = filtered.sort_values(by=sort_cols, ascending=ascending_rules)

    # Liste des colonnes cibles
    curr_col = (
        "currency"
        if "currency" in results.columns
        else ("devise" if "devise" in results.columns else None)
    )

    target_cols = [
        "name",
        "city",
        "country",
        "cuisine",
        price_col,
        curr_col,
        rating_col,
        "predicted_rating",
    ]

    existing_cols = [c for c in target_cols if c and c in results.columns]

    return results[existing_cols].head(top_n)


# --- INTERFACE UTILISATEUR ---
st.title("🤖 Machine Learning & Recommandations")

# 🔄 BOUTON DE RAFRAÎCHISSEMENT
if st.button("🔄 Rafraîchir les données depuis PostgreSQL"):
    if "df" in st.session_state:
        del st.session_state["df"]
    st.cache_data.clear()
    st.rerun()

# Chargement du DataFrame
df = get_or_load_dataframe()

if not df.empty:
    tab_clustering, tab_recommendation = st.tabs(
        ["📊 Clustering des Restaurants", "🎯 Système de Recommandation"]
    )

    # -------------------------------------------------------------
    # TAB 1 : CLUSTERING (K-MEANS)
    # -------------------------------------------------------------
    with tab_clustering:
        st.subheader("📊 Segmentation des restaurants par Clustering (K-Means)")

        num_clusters = st.slider("Nombre de groupes (clusters) :", 2, 6, 3)

        features = [
            col
            for col in ["rating", "predicted_rating", "reviews_count", "avg_price"]
            if col in df.columns
        ]

        if len(features) >= 2:
            df_cluster = df.dropna(subset=features).copy()

            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(df_cluster[features])

            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            df_cluster["Cluster"] = kmeans.fit_predict(scaled_data)
            df_cluster["Cluster"] = df_cluster["Cluster"].astype(str)

            # Palette de couleurs profondes à fort contraste
            cluster_colors = ["#8C6B1B", "#1E3A8A", "#991B1B", "#065F46", "#5B21B6", "#D97706"]

            fig = px.scatter(
                df_cluster,
                x=features[0],
                y=features[1],
                color="Cluster",
                hover_data=["name", "city", "cuisine"],
                title=f"<b>Clustering K-Means ({num_clusters} Clusters)</b>",
                color_discrete_sequence=cluster_colors,
                template="plotly_white",
            )

            # --- OPTIMISATION DE LA NETTETÉ DE LA FIGURE ---
            fig.update_traces(
                marker=dict(
                    size=10,
                    opacity=0.9,
                    line=dict(width=1, color="#1A1A1A")  # Contour sombre net autour des points
                )
            )

            fig.update_layout(
                title_font=dict(size=18, color="#1A1A1A"),
                font=dict(color="#2D2D2E", size=13),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#FFFFFF",
                xaxis=dict(
                    title=f"<b>{features[0]}</b>",
                    title_font=dict(size=14, color="#1A1A1A"),
                    showgrid=True,
                    gridcolor="#E2E8F0",
                    zeroline=False,
                    linecolor="#1A1A1A",
                    linewidth=1.5,
                ),
                yaxis=dict(
                    title=f"<b>{features[1]}</b>",
                    title_font=dict(size=14, color="#1A1A1A"),
                    showgrid=True,
                    gridcolor="#E2E8F0",
                    zeroline=False,
                    linecolor="#1A1A1A",
                    linewidth=1.5,
                ),
                legend=dict(
                    title_text="<b>Cluster</b>",
                    bordercolor="#CBD5E1",
                    borderwidth=1,
                    bgcolor="#FFFFFF"
                ),
                height=520,
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(
                "Nombre insuffisant de colonnes numériques pour faire le clustering."
            )

    # -------------------------------------------------------------
    # TAB 2 : SYSTÈME DE RECOMMANDATION (PRÉFÉRENCES UTILISATEUR)
    # -------------------------------------------------------------
    with tab_recommendation:
        st.subheader(
            "🎯 Recommandation de Restaurants selon vos Préférences"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            country_options = ["Tous"] + list(COUNTRIES_CITIES.keys())
            selected_country = st.selectbox("🌍 Pays :", country_options)

        with col2:
            if selected_country != "Tous":
                city_options = ["Toutes"] + COUNTRIES_CITIES[selected_country]
            else:
                all_cities = []
                for c_list in COUNTRIES_CITIES.values():
                    all_cities.extend(c_list)
                city_options = ["Toutes"] + sorted(list(set(all_cities)))

            selected_city = st.selectbox("🏙️ Ville :", city_options)

        with col3:
            if "cuisine" in df.columns:
                db_cuisines = (
                    df["cuisine"]
                    .dropna()
                    .astype(str)
                    .str.strip()
                    .unique()
                    .tolist()
                )
                db_cuisines = sorted([c for c in db_cuisines if c != ""])
                cuisine_options = ["Toutes"] + db_cuisines
            else:
                cuisine_options = ["Toutes"]

            selected_cuisine = st.selectbox("🍳 Type de Cuisine :", cuisine_options)

        col4, col5 = st.columns(2)

        with col4:
            price_col = (
                "avg_price"
                if "avg_price" in df.columns
                else ("price_numeric" if "price_numeric" in df.columns else None)
            )
            if price_col and df[price_col].notna().any():
                max_p = float(df[price_col].max())
                selected_price = st.slider(
                    "💰 Prix Maximum :",
                    min_value=0.0,
                    max_value=max_p,
                    value=max_p,
                    step=5.0,
                )
            else:
                selected_price = None

        with col5:
            top_n = st.slider(
                "🔝 Nombre de résultats :",
                min_value=1,
                max_value=20,
                value=5,
            )

        # Exécution de la recommandation
        recommendations = recommend_restaurants(
            df=df,
            city=selected_city if selected_city != "Toutes" else None,
            country=selected_country if selected_country != "Tous" else None,
            cuisine=selected_cuisine,
            max_price=selected_price,
            top_n=top_n,
        )

        st.markdown("---")

        if not recommendations.empty:
            st.success(
                f"🌟 **{len(recommendations)}** meilleurs restaurants recommandés"
                " selon vos critères :"
            )

            # FORMATAGE DU PRIX AVEC DEVISE POUR L'AFFICHAGE
            display_df = recommendations.copy()

            p_col = (
                "avg_price"
                if "avg_price" in display_df.columns
                else ("price_numeric" if "price_numeric" in display_df.columns else None)
            )

            if p_col and p_col in display_df.columns:

                def format_price_with_currency(row):
                    val = row[p_col]
                    if pd.isna(val) or val == 0:
                        return "N/A"

                    curr = row.get("currency") or row.get("devise")

                    if not curr or pd.isna(curr):
                        country_val = row.get("country", "")
                        curr = CURRENCY_MAP.get(country_val, "")

                    return f"{val:.2f} {curr}".strip()

                display_df["Prix Moyen"] = display_df.apply(
                    format_price_with_currency, axis=1
                )

                cols_to_drop = [
                    c for c in [p_col, "currency", "devise"] if c in display_df.columns
                ]
                display_df = display_df.drop(columns=cols_to_drop)

            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning(
                "⚠️ Aucun restaurant ne correspond exactement à ces critères de"
                " recherche."
            )

else:
    st.warning("⚠️ Aucune donnée disponible pour le Machine Learning.")