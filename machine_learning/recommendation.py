import pandas as pd
import numpy as np

def recommend_restaurants(
    df: pd.DataFrame, 
    city: str, 
    country: str = None,
    cuisine: str = None, 
    max_price: float = None,
    top_n: int = 5
) -> pd.DataFrame:
    """
    Recommande les meilleurs restaurants en donnant la priorité aux notes réelles,
    tout en proposant des estimations IA si aucune note réelle n'est disponible.
    """
    if df.empty:
        return pd.DataFrame()

    # 1. Filtre géographique par Ville
    filtered = df[df['city'].str.lower() == city.lower()].copy()
    
    # 2. Filtre par Pays si fourni
    if country and 'country' in filtered.columns:
        filtered = filtered[filtered['country'].str.lower() == country.lower()]

    # 3. Filtre par Cuisine
    if cuisine and cuisine != "Toutes" and 'cuisine' in filtered.columns:
        filtered = filtered[filtered['cuisine'].str.lower().str.contains(cuisine.lower(), na=False)]

    # 4. Filtre par Prix
    if max_price is not None and 'price_numeric' in filtered.columns:
        filtered = filtered[filtered['price_numeric'] <= max_price]

    if filtered.empty:
        print(f"Aucun restaurant trouvé pour : {city}")
        return pd.DataFrame()

    # Sélection de la meilleure note disponible (réelle en priorité, sinon prédite)
    rating_col = 'final_rating' if 'final_rating' in filtered.columns else 'rating'
    
    # Calcul du score de recommandation
    reviews_log = np.log1p(filtered['reviews_count'].fillna(0))
    filtered['recommendation_score'] = (filtered[rating_col].fillna(0) * (reviews_log + 1)).round(2)

    # Tri : Priorité aux notes réelles (`is_rating_estimated` == False d'abord), puis par Score
    sort_cols = ['is_rating_estimated', 'recommendation_score', rating_col]
    ascending_rules = [True, False, False]

    results = filtered.sort_values(by=sort_cols, ascending=ascending_rules)
    
    cols = ['name', 'city', 'country', 'cuisine', rating_col, 'reviews_count', 'is_rating_estimated', 'recommendation_score']
    existing_cols = [c for c in cols if c in results.columns]
    
    return results[existing_cols].head(top_n)