import os
import sys
import pandas as pd
import streamlit as st

# Setup des chemins d'import
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(DASHBOARD_DIR)

for path in [DASHBOARD_DIR, PROJECT_ROOT]:
  if path not in sys.path:
    sys.path.insert(0, path)

# Imports sécurisés des éléments existants
try:
  from charts.kpis import (
      chart_cuisine_distribution,
      chart_rating_distribution,
      chart_restaurants_by_city,
  )
  from components.map import render_map
  from components.sidebar import render_sidebar
except ImportError:
  from dashboard.charts.kpis import (
      chart_cuisine_distribution,
      chart_rating_distribution,
      chart_restaurants_by_city,
  )
  from dashboard.components.map import render_map
  from dashboard.components.sidebar import render_sidebar

st.set_page_config(
    page_title="Dashboard Analytique", page_icon="📊", layout="wide"
)

st.title("📊 Tableau de Bord Analytique")

df = st.session_state.get("df", pd.DataFrame())

if not df.empty:
  filtered_df = render_sidebar(df)

  # KPI Cards intégrées directement
  c1, c2, c3, c4 = st.columns(4)
  c1.metric("Total Restaurants", f"{len(filtered_df):,}")
  c2.metric(
      "Note Moyenne",
      f"{filtered_df['rating'].mean():.2f} ⭐"
      if 'rating' in filtered_df.columns
      else "N/A",
  )
  c3.metric(
      "Villes",
      filtered_df['city'].nunique() if 'city' in filtered_df.columns else 0,
  )
  c4.metric(
      "Cuisines",
      filtered_df['cuisine'].nunique()
      if 'cuisine' in filtered_df.columns
      else 0,
  )

  st.markdown("---")

  # Graphiques
  col_left, col_right = st.columns(2)
  with col_left:
    st.plotly_chart(
        chart_restaurants_by_city(filtered_df), use_container_width=True
    )
  with col_right:
    st.plotly_chart(
        chart_cuisine_distribution(filtered_df), use_container_width=True
    )

  # Carte
  st.subheader("🗺️ Carte Interactive")
  render_map(filtered_df)

  # Notes
  st.plotly_chart(
      chart_rating_distribution(filtered_df), use_container_width=True
  )

  # Tableau Top 10
  st.subheader("🏆 Classement des Meilleurs Restaurants")
  cols = [
      c
      for c in [
          'name',
          'city',
          'cuisine',
          'rating',
          'reviews_count',
          'avg_price',
      ]
      if c in filtered_df.columns
  ]
  st.dataframe(
      filtered_df[cols].sort_values(by='rating', ascending=False).head(10),
      use_container_width=True,
  )

else:
  st.warning(
      "⚠️ Aucune donnée disponible. Veuillez repasser par la page d'accueil"
      " (`app`)."
  )