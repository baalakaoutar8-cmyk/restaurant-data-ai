import plotly.express as px
import pandas as pd

def plot_rating_vs_price(df: pd.DataFrame):
    """Génère un graphique Boxplot de la note selon la tranche de prix."""
    df_clean = df.dropna(subset=['price_range', 'rating']).copy()
    
    fig = px.box(
        df_clean, 
        x='price_range', 
        y='rating',
        color='price_range',
        title="Distribution des Notes par Tranche de Prix",
        labels={'price_range': 'Gamme de Prix', 'rating': 'Note (Rating)'},
        template='plotly_white'
    )
    return fig


def plot_geographic_distribution(df: pd.DataFrame):
    """Génère une carte interactive des restaurants."""
    df_clean = df.dropna(subset=['latitude', 'longitude']).copy()
    
    size_col = "reviews_count" if "reviews_count" in df_clean.columns else None
    
    fig = px.scatter_mapbox(
        df_clean,
        lat="latitude",
        lon="longitude",
        hover_name="name" if "name" in df_clean.columns else None,
        hover_data=["city", "rating", "price_range"],
        color="rating" if "rating" in df_clean.columns else None,
        size=size_col,
        color_continuous_scale=px.colors.cyclical.IceFire,
        size_max=15,
        zoom=5,
        title="Répartition Géographique des Restaurants"
    )
    fig.update_layout(mapbox_style="open-street-map")
    return fig