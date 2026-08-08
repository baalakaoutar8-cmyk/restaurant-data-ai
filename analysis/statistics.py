import pandas as pd
import numpy as np

def get_rating_price_correlation(df: pd.DataFrame) -> float:
    """Calcule la corrélation entre la gamme de prix et la note moyenne."""
    if 'price_range' not in df.columns or 'rating' not in df.columns:
        return 0.0

    df_clean = df.dropna(subset=['price_range', 'rating']).copy()
    
    # Nettoyage et conversion des valeurs de price_range ($$, numeric, etc.)
    def parse_price(val):
        val_str = str(val).strip()
        if '$' in val_str:
            return float(val_str.count('$'))
        elif val_str.replace('.', '', 1).isdigit():
            return float(val_str)
        return np.nan

    df_clean['price_numeric'] = df_clean['price_range'].apply(parse_price)
    df_valid = df_clean.dropna(subset=['price_numeric', 'rating'])
    
    if len(df_valid) < 2:
        return 0.0

    return float(df_valid['rating'].corr(df_valid['price_numeric']))


def top_rated_cities(df: pd.DataFrame, min_reviews_count: int = 10) -> pd.DataFrame:
    """Retourne les villes les mieux notées (filtrées par un minimum d'avis)."""
    if 'city' not in df.columns or 'rating' not in df.columns:
        return pd.DataFrame()

    total_reviews_col = 'reviews_count' if 'reviews_count' in df.columns else 'rating'

    city_stats = df.groupby('city').agg(
        avg_rating=('rating', 'mean'),
        total_restaurants=('id', 'count'),
        total_reviews=(total_reviews_col, 'sum')
    ).reset_index()
    
    filtered = city_stats[city_stats['total_reviews'] >= min_reviews_count]
    return filtered.sort_values(by='avg_rating', ascending=False)


def cuisine_popularity(df: pd.DataFrame) -> pd.DataFrame:
    """Analyse la popularité et la note moyenne par type de cuisine."""
    if 'cuisine' not in df.columns:
        return pd.DataFrame()

    df_clean = df.dropna(subset=['cuisine']).copy()
    df_exploded = df_clean.assign(cuisine=df_clean['cuisine'].astype(str).str.split(',')).explode('cuisine')
    df_exploded['cuisine'] = df_exploded['cuisine'].str.strip()
    
    cuisine_stats = df_exploded.groupby('cuisine').agg(
        restaurant_count=('id', 'count'),
        avg_rating=('rating', 'mean')
    ).reset_index()
    
    return cuisine_stats.sort_values(by='restaurant_count', ascending=False)