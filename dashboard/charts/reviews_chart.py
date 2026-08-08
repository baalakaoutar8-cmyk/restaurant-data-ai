import plotly.express as px
import pandas as pd

def chart_reviews_distribution(df: pd.DataFrame):
    """Top 15 des restaurants les plus évalués"""
    if df.empty or 'reviews_count' not in df.columns:
        return px.bar(title="Top restaurants par avis (Aucune donnée)")
        
    top_reviews = df.nlargest(15, 'reviews_count')
    fig = px.bar(
        top_reviews,
        x='reviews_count',
        y='name',
        orientation='h',
        title="Top 15 des restaurants les plus évalués",
        color='reviews_count',
        color_continuous_scale='Blues',
        labels={'reviews_count': "Nombre d'avis", 'name': "Restaurant"}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(l=20, r=20, t=40, b=20))
    return fig