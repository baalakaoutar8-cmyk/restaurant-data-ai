import pandas as pd

def compute_global_kpis(df_restaurants: pd.DataFrame, df_reviews: pd.DataFrame = None) -> dict:
    """Calcule les indicateurs clés de performance (KPIs)."""
    kpis = {
        "total_restaurants": int(df_restaurants['id'].nunique()) if 'id' in df_restaurants.columns else len(df_restaurants),
        "total_cities": int(df_restaurants['city'].nunique()) if 'city' in df_restaurants.columns else 0,
        "total_countries": int(df_restaurants['country'].nunique()) if 'country' in df_restaurants.columns else 0,
        "average_global_rating": round(float(df_restaurants['rating'].mean()), 2) if 'rating' in df_restaurants.columns else 0.0,
        "total_reviews_count": int(df_restaurants['reviews_count'].sum()) if 'reviews_count' in df_restaurants.columns else 0
    }
    
    if df_reviews is not None and not df_reviews.empty:
        kpis["total_individual_reviews"] = int(len(df_reviews))
        if 'owner_response' in df_reviews.columns:
            response_rate = (df_reviews['owner_response'].notna().sum() / len(df_reviews)) * 100
            kpis["owner_response_rate_pct"] = round(float(response_rate), 2)
            
    return kpis