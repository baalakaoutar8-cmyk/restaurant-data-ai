import folium
from folium.plugins import FastMarkerCluster
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


def render_map(df, max_markers=None):
    """Affiche la carte des restaurants.

    Aucun message d'information ou de succès ne s'affiche au-dessus de la
    carte.
    """
    if df.empty or "latitude" not in df.columns or "longitude" not in df.columns:
        st.warning("⚠️ Aucune donnée géographique disponible.")
        return

    # 1. Nettoyage et conversion des coordonnées GPS
    valid_df = df.copy()
    valid_df["latitude"] = pd.to_numeric(
        valid_df["latitude"], errors="coerce"
    )
    valid_df["longitude"] = pd.to_numeric(
        valid_df["longitude"], errors="coerce"
    )

    # Filtrage des coordonnées valides
    valid_df = valid_df.dropna(subset=["latitude", "longitude"])
    valid_df = valid_df[
        (valid_df["latitude"] != 0)
        & (valid_df["longitude"] != 0)
        & (valid_df["latitude"].between(-90, 90))
        & (valid_df["longitude"].between(-180, 180))
    ]

    if valid_df.empty:
        st.warning("⚠️ Aucune coordonnée GPS valide à afficher.")
        return

    # Limite max_markers (sans message d'information)
    if max_markers is not None and len(valid_df) > max_markers:
        display_df = valid_df.head(max_markers)
    else:
        display_df = valid_df

    # 2. Preparation des données [lat, lon, nom, note]
    locations_data = []
    for _, row in display_df.iterrows():
        rating = row.get("rating", None)
        rating_str = f"{rating:.1f} ⭐" if pd.notna(rating) else "N/A"

        name_clean = (
            str(row.get("name", "Restaurant"))
            .strip()
            .replace("\n", " ")
            .replace("\r", "")
        )

        locations_data.append([
            float(row["latitude"]),
            float(row["longitude"]),
            name_clean,
            rating_str,
        ])

    # 3. Callback JavaScript Folium
    callback = """
    function (row) {
        var lat = row[0];
        var lon = row[1];
        var name = row[2];
        var rating = row[3];

        var marker = L.marker(new L.LatLng(lat, lon));
        var popupContent = '<div style="font-family: sans-serif; font-size: 13px; color: #1E1E1E;">' +
                           '<b style="font-size: 14px;">' + name + '</b><br>' +
                           '<span style="color: #d97706; font-weight: bold; font-size: 12px;">' + rating + '</span>' +
                           '</div>';

        marker.bindPopup(popupContent, {maxWidth: 220});
        return marker;
    };
    """

    # 4. Création de la carte
    center_lat = display_df["latitude"].mean()
    center_lon = display_df["longitude"].mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=5,
        tiles="CartoDB dark_matter",
    )

    # 5. Ajout des marqueurs
    FastMarkerCluster(data=locations_data, callback=callback).add_to(m)

    # 6. Rendu HTML
    components.html(m._repr_html_(), height=560)