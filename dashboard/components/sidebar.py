import streamlit as st
import pandas as pd

def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """Affiche les filtres dans la barre latérale et retourne le DataFrame filtré"""
    st.sidebar.header("🔍 Filtres Dynamiques")

    if df.empty:
        return df

    # Filtre Ville
    cities = sorted(df['city'].dropna().unique()) if 'city' in df.columns else []
    selected_cities = st.sidebar.multiselect("Villes", options=cities)

    # Filtre Cuisine
    cuisines = sorted(df['cuisine'].dropna().unique()) if 'cuisine' in df.columns else []
    selected_cuisines = st.sidebar.multiselect("Types de Cuisine", options=cuisines)

    # Options spécifiques
    only_delivery = st.sidebar.checkbox("🛵 Option Livraison uniquement")
    only_family = st.sidebar.checkbox("👨‍👩‍👧‍👦 Adapté aux familles uniquement")

    # Application des filtres
    filtered_df = df.copy()

    if selected_cities:
        filtered_df = filtered_df[filtered_df['city'].isin(selected_cities)]
    if selected_cuisines:
        filtered_df = filtered_df[filtered_df['cuisine'].isin(selected_cuisines)]
    if only_delivery and 'has_delivery' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['has_delivery'] == True]
    if only_family and 'is_family_friendly' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['is_family_friendly'] == True]

    return filtered_df