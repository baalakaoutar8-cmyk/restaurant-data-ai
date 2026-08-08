import os
import urllib.parse
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

# Importer le module de thème Luxe
try:
    from dashboard.theme import apply_luxury_theme, render_kpi_card
except ImportError:

    def apply_luxury_theme():
        pass

    def render_kpi_card(t, v, s=""):
        st.metric(t, v, s)


# 1. Configuration de la page
st.set_page_config(
    page_title="Annuaire & Classement | Elite Dining",
    page_icon="👑",
    layout="wide",
)

# 2. Application du thème
apply_luxury_theme()

# --- INJECTION CSS : CONTOURS ET TEXTES EN DORÉ TRÈS FONCÉ (FOND ENTIÈREMENT PRESERVÉ) ---
st.markdown(
    """
<style>
/* Contour et style des menus déroulants (Filtres) */
div[data-baseweb="select"] > div {
    border: 2px solid #654D0F !important;
    border-radius: 8px !important;
}

/* Contour et style des cartes KPI */
div[data-testid="stMetric"] {
    border: 2px solid #654D0F !important;
    border-radius: 10px !important;
    padding: 15px !important;
}

/* Titres des KPI */
div[data-testid="stMetricLabel"] p {
    color: #654D0F !important;
    font-weight: 800 !important;
}

/* Chiffres et valeurs des KPI */
div[data-testid="stMetricValue"] div {
    color: #654D0F !important;
    font-weight: 800 !important;
}

/* Sous-titres sous les cartes KPI */
div[data-testid="stMetric"] p, div[data-testid="stMetric"] span, div[data-testid="stMetric"] small {
    color: #654D0F !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- EN-TÊTE ---
st.markdown(
    "<h1 style='text-align: center; margin-bottom: 5px;'>✨ ANNUAIRE & SÉLECTION DE LUXE</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #654D0F; margin-bottom: 30px; font-weight: 800; letter-spacing: 1.5px;'>EXPLOREZ LES MEILLEURES TABLES DU MAROC ET DU GOLFE</p>",
    unsafe_allow_html=True,
)


# --- FONCTIONS BDD ---
@st.cache_resource
def get_db_engine():
    """Maintient le moteur de connexion PostgreSQL en cache global."""
    load_dotenv()
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
    """Récupère les données en direct si session_state est vide."""
    engine = get_db_engine()
    return pd.read_sql("SELECT * FROM restaurants;", engine)


# Initialisation ou restauration des données
if "df" not in st.session_state or st.session_state["df"].empty:
    try:
        st.session_state["df"] = load_data_from_db()
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données : {e}")

df = st.session_state.get("df", pd.DataFrame()).copy()

if not df.empty:
    ALLOWED_COUNTRIES = [
        "MOROCCO",
        "United Arab Emirates",
        "Saudi Arabia",
        "Qatar",
        "Kuwait",
        "Bahrain",
    ]

    CURRENCY_MAP = {
        "MOROCCO": "MAD",
        "United Arab Emirates": "AED",
        "Saudi Arabia": "SAR",
        "Qatar": "QAR",
        "Kuwait": "KWD",
        "Bahrain": "BHD",
    }

    # --- 1. FILTRES DYNAMIQUES ---
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        selected_country = st.selectbox(
            "Filtrer par Pays :",
            ["Tous"] + ALLOWED_COUNTRIES,
            key="select_country_resto",
        )

    # Filtrage pays
    df_filtered = df.copy()
    allowed_upper = [c.upper() for c in ALLOWED_COUNTRIES]

    if selected_country != "Tous":
        df_filtered = df_filtered[
            df_filtered["country"].astype(str).str.upper() == selected_country.upper()
        ]
    else:
        df_filtered = df_filtered[
            df_filtered["country"].astype(str).str.upper().isin(allowed_upper)
        ]

    with col2:
        if selected_country != "Tous":
            cities = ["Toutes"] + sorted([
                str(c)
                for c in df_filtered["city"].dropna().unique()
                if str(c).strip() != "" and str(c) != "Not Existed"
            ])
            selected_city = st.selectbox(
                "Filtrer par Ville :", cities, key="select_city_resto"
            )
            if selected_city != "Toutes":
                df_filtered = df_filtered[df_filtered["city"] == selected_city]

    with col3:
        sort_option = st.selectbox(
            "Trier par :",
            ["Note Reelle (rating)", "Nombre d'avis", "Prix Moyen"],
            index=0,
            key="select_sort_resto",
        )

    # --- 2. CARTES KPI LUXE ---
    st.markdown("<br>", unsafe_allow_html=True)
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

    avg_note = (
        f"{df_filtered['rating'].mean():.2f} / 5"
        if "rating" in df_filtered and not df_filtered["rating"].isna().all()
        else "N/A"
    )
    total_restos = f"{len(df_filtered):,}"
    selection_label = (
        selected_country if selected_country != "Tous" else "Maroc & Moyen-Orient"
    )

    with kpi_col1:
        render_kpi_card("Établissements", total_restos, "Restaurants répertoriés")
    with kpi_col2:
        render_kpi_card("Note Moyenne", avg_note, "Satisfaction globale")
    with kpi_col3:
        render_kpi_card("Sélection", selection_label, "Zone géographique")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. APPLICATION DU TRI ---
    if sort_option == "Note Reelle (rating)":
        df_filtered = df_filtered.sort_values(
            by="rating", ascending=False, na_position="last"
        )
    elif sort_option == "Nombre d'avis":
        df_filtered = df_filtered.sort_values(
            by="reviews_count", ascending=False, na_position="last"
        )
    elif sort_option == "Prix Moyen":
        df_filtered = df_filtered.sort_values(
            by="avg_price", ascending=True, na_position="last"
        )

    # --- 4. NETTOYAGE ET COLONNES ---
    cols_to_drop = [
        "price_range",
        "source",
        "created_at",
        "is_rating_estimated",
        "is_suspicious",
        "opening_hours",
        "cluster_label",
        "reviews_count",
    ]
    df_display = df_filtered.drop(
        columns=[c for c in cols_to_drop if c in df_filtered.columns]
    )

    if "id" in df_display.columns:
        cols = ["id"] + [c for c in df_display.columns if c != "id"]
        df_display = df_display[cols]

    # --- 5. FORMATAGE DES PRIX ---
    def format_price(row):
        price = row.get("avg_price")
        country = str(row.get("country", "")).strip().upper()
        if pd.isna(price) or price is None:
            return "Not Existed"

        currency = "MAD"
        for c_name, c_curr in CURRENCY_MAP.items():
            if c_name.upper() == country:
                currency = c_curr
                break
        return f"{price:.2f} {currency}"

    if "avg_price" in df_display.columns:
        df_display["avg_price"] = df_display.apply(format_price, axis=1)

    text_cols = df_display.select_dtypes(include=["object"]).columns
    df_display[text_cols] = df_display[text_cols].fillna("Not Existed")
    df_display[text_cols] = df_display[text_cols].replace(
        ["None", "none", "nan", "NaN", ""], "Not Existed"
    )

    # --- 6. AFFICHAGE DU TABLEAU GRAND FORMAT ---
    st.dataframe(
        df_display,
        use_container_width=True,
        height=650,
        hide_index=True,
    )

else:
    st.warning("Aucune donnée disponible dans la base de données.")