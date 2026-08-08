# dashboard/charts/kpis.py
import plotly.express as px
import pandas as pd

def chart_restaurants_by_city(df: pd.DataFrame):
    """Graphique : Nombre de restaurants par ville"""
    city_counts = df['city'].value_counts().reset_index()
    city_counts.columns = ['Ville', 'Nombre']
    fig = px.bar(
        city_counts.head(10), 
        x='Nombre', 
        y='Ville', 
        orientation='h',
        title="Top 10 Villes par nombre de restaurants",
        color='Nombre',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig

def chart_cuisine_distribution(df: pd.DataFrame):
    """Graphique : Répartition des types de cuisine"""
    cuisine_counts = df['cuisine'].value_counts().reset_index()
    cuisine_counts.columns = ['Cuisine', 'Nombre']
    fig = px.pie(
        cuisine_counts.head(8), 
        names='Cuisine', 
        values='Nombre',
        title="Répartition des types de cuisine",
        hole=0.4
    )
    return fig

def chart_rating_distribution(df: pd.DataFrame):
    """Graphique : Distribution des notes moyennes"""
    fig = px.histogram(
        df, 
        x='rating', 
        nbins=20, 
        title="Distribution des notes réelles",
        color_discrete_sequence=['#FF9900']
    )
    fig.update_layout(xaxis_title="Note sur 5", yaxis_title="Nombre de restaurants")
    return fig