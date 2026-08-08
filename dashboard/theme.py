import streamlit as st


def apply_luxury_theme():
  """Injecte le thème Luxe Ivoire, Sable & Or méticuleusement extrait de votre capture."""
  st.markdown(
      """
    <style>
    /* 1. ARRIÈRE-PLAN PRINCIPAL (Blanc Lumineux) */
    [data-testid="stAppViewContainer"], .main {
        background-color: #FFFFFF !important;
        color: #2D2D2E !important;
    }

    /* 2. BARRE LATÉRALE (Sable / Beige Champagne) */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
        background-color: #E7E1C5 !important;
        border-right: 1px solid #D8CEAA !important;
    }

    [data-testid="stSidebar"] * {
        color: #333333 !important;
    }

    /* 3. TITRES & SOUS-TITRES (Or Chaud / Ambre) */
    h1, h2, h3 {
        color: #CBB265 !important;
        font-weight: 700 !important;
    }

    .stMarkdown p strong {
        color: #CBB265 !important;
    }

    /* 4. ZONE BANNIÈRE / MESSAGES D'ACCUEIL (Gris Anthracite) */
    .stAlert, div[data-testid="stNotification"] {
        background-color: #57575A !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
    }

    /* 5. BOUTONS & PILLS DE SUGGESTION (Noir Anthracite & Or) */
    div.stButton > button {
        background-color: #343436 !important;
        color: #FFFFFF !important;
        border: 1px solid #343436 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button:hover {
        background-color: #CBB265 !important;
        color: #FFFFFF !important;
        border-color: #CBB265 !important;
    }

    /* 6. CHAMP DE SAISIE / CHAT INPUT (Beige Sable) */
    [data-testid="stChatInput"], 
    .stTextInput input, 
    div[data-baseweb="select"] > div {
        background-color: #E7E1C5 !important;
        color: #2D2D2E !important;
        border: 1px solid #D8CEAA !important;
        border-radius: 10px !important;
    }

    /* 7. CARTES KPI LUXE (Fond Sable Clair avec bordure Or) */
    .kpi-card-luxury {
        background-color: #F7F5EC;
        border: 1px solid #E7E1C5;
        border-top: 3px solid #CBB265;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    }

    .kpi-title {
        color: #7A7A7A !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .kpi-value {
        color: #CBB265 !important;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 4px 0;
    }

    .kpi-subtitle {
        color: #A38B42 !important;
        font-size: 0.8rem;
        font-style: italic;
    }

    /* 8. TABLEAUX DATAFRAME */
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E7E1C5 !important;
        border-radius: 10px !important;
    }

    /* MASQUER LE BRANDING STREAMLIT */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
      unsafe_allow_html=True,
  )


def render_kpi_card(title: str, value: str, subtitle: str = ""):
  """Affiche une carte KPI personnalisée au style Ivoire & Or."""
  st.markdown(
      f"""
        <div class="kpi-card-luxury">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-subtitle">{subtitle}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )