import pandas as pd
import streamlit as st


def render_kpi_cards(df: pd.DataFrame):
  """Affiche les cartes d'indicateurs clés (KPIs)"""
  if df.empty:
    return

  total_restaurants = len(df)
  avg_rating = df['rating'].mean() if 'rating' in df.columns else 0
  total_cities = df['city'].nunique() if 'city' in df.columns else 0
  total_cuisines = df['cuisine'].nunique() if 'cuisine' in df.columns else 0

  col1, col2, col3, col4 = st.columns(4)

  with col1:
    st.metric("Total Restaurants", f"{total_restaurants:,}")
  with col2:
    st.metric(
        "Note Moyenne",
        f"{avg_rating:.2f} ⭐" if avg_rating else "N/A",
    )
  with col3:
    st.metric("Villes Couvertes", total_cities)
  with col4:
    st.metric("Types de Cuisine", total_cuisines)