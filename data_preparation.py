import pandas as pd #type:ignore
import numpy as np #type:ignore
from sqlalchemy import create_engine #type:ignore
# 1. Connexion à la base PostgreSQL via SQLAlchemy
DB_URI = "postgresql+psycopg2://postgres:1234@localhost:5432/restaurants_db"
engine = create_engine(DB_URI)

def load_raw_data():
    """Extraction des données brutes"""
    query = "SELECT * FROM restaurants;"
    df = pd.read_sql(query, engine)
    print(f" Data brute chargée : {len(df)} lignes.")
    return df

def clean_data(df):
    """Module DATA PREPARATION : Nettoyage et Imputation"""
    df_clean = df.copy()

    # Nettoyage des chaînes de caractères
    df_clean['name'] = df_clean['name'].str.strip()
    df_clean['city'] = df_clean['city'].str.strip().str.title()
    df_clean['country'] = df_clean['country'].str.strip().str.upper()

    # Remplissage des notes manquantes par la médiane par pays/ville
    df_clean['rating'] = df_clean.groupby('country')['rating'].transform(lambda x: x.fillna(x.median()))
    df_clean['rating'] = df_clean['rating'].fillna(df_clean['rating'].median()) # Si le pays complet est vide

    # Gestion du nombre d'avis
    df_clean['reviews_count'] = df_clean['reviews_count'].fillna(0).astype(int)

    print(" Nettoyage et imputation terminés.")
    return df_clean

def build_features(df):
    """Module FEATURE ENGINEERING : Création de variables pour l'IA"""
    df_feat = df.copy()

    # 1. Conversion du Price Range ($$, $$$, $$$$) en score numérique
    price_map = {
        '$': 1, '€': 1, 'Cheap': 1,
        '$$': 2, '€€': 2, 'Moderate': 2,
        '$$$': 3, '€€€': 3, 'Expensive': 3,
        '$$$$': 4, '€€€€': 4, 'Very Expensive': 4
    }
    df_feat['price_numeric'] = df_feat['price_range'].map(price_map).fillna(2) # Valeur par défaut: Moderate (2)

    # 2. Variable complexe : Score de Popularité (Combinaison log des avis et note)
    # NumPy log1p évite log(0) si un restaurant a 0 avis
    df_feat['popularity_score'] = np.log1p(df_feat['reviews_count']) * df_feat['rating']

    # 3. Traitement géographique : Indicateur si coordonnées GPS présentes
    df_feat['has_coordinates'] = np.where(df_feat['latitude'].notna() & df_feat['longitude'].notna(), 1, 0)

    # 4. Encodage One-Hot pour le Machine Learning (Transformation des catégories en colonnes 0/1)
    # Utile pour les algorithmes comme K-Means ou Régression
    df_encoded = pd.get_dummies(df_feat, columns=['country'], prefix='country', drop_first=False)

    print(" Feature Engineering terminé (Nouvelles variables créées : price_numeric, popularity_score, etc.).")
    return df_encoded

if __name__ == "__main__":
    # Exécution du pipeline
    raw_df = load_raw_data()
    clean_df = clean_data(raw_df)
    final_df = build_features(clean_df)

    # Sauvegarde du dataset prêt pour le Machine Learning
    final_df.to_csv("data_ready_for_ml.csv", index=False)
    print("\n Base préparée sauvegardée sous 'data_ready_for_ml.csv' !")