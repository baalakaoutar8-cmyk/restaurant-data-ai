import pandas as pd
import numpy as np

def clean_data_for_ml(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie et prépare le jeu de données des restaurants pour les algorithmes ML.
    """
    df_clean = df.copy()

    # 1. Nettoyage des noms corrompus (ex: "(1,490 reviews)")
    if 'name' in df_clean.columns:
        df_clean = df_clean[~df_clean['name'].str.contains(r'\(.*reviews\)', case=False, na=False)].copy()

    # 2. Conversion du prix texte en valeur numérique (ex: "$$$" -> 3)
    if 'price_range' in df_clean.columns:
        price_map = {'$': 1, '$$': 2, '$$$': 3, '$$$$': 4}
        df_clean['price_numeric'] = df_clean['price_range'].map(price_map).fillna(1)
    else:
        df_clean['price_numeric'] = 1

    # 3. Conversion propre des coordonnées géographiques
    if 'latitude' in df_clean.columns:
        df_clean['latitude'] = pd.to_numeric(df_clean['latitude'], errors='coerce').fillna(0.0)
    else:
        df_clean['latitude'] = 0.0

    if 'longitude' in df_clean.columns:
        df_clean['longitude'] = pd.to_numeric(df_clean['longitude'], errors='coerce').fillna(0.0)
    else:
        df_clean['longitude'] = 0.0

    # 4. Conversion des nombres d'avis et des notes
    if 'reviews_count' in df_clean.columns:
        df_clean['reviews_count'] = pd.to_numeric(df_clean['reviews_count'], errors='coerce').fillna(0)
    else:
        df_clean['reviews_count'] = 0

    if 'rating' in df_clean.columns:
        df_clean['rating'] = pd.to_numeric(df_clean['rating'], errors='coerce')

    # 5. Harmonisation de la ville
    if 'city' in df_clean.columns:
        df_clean['city'] = df_clean['city'].astype(str).str.strip()

    return df_clean