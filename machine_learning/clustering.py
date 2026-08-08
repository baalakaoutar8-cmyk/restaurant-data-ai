import os
import joblib
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from machine_learning.preprocessing import clean_data_for_ml

def cluster_restaurants(df: pd.DataFrame, n_clusters: int = 2) -> pd.DataFrame:
    df_clean = clean_data_for_ml(df)
    
    rating_col = 'final_rating' if 'final_rating' in df_clean.columns else 'rating'
    
    df_clean['log_reviews'] = np.log1p(df_clean['reviews_count'].fillna(0))
    X = df_clean[[rating_col, 'log_reviews', 'price_numeric']].fillna(0)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_clean['cluster'] = kmeans.fit_predict(X)

    cluster_means = df_clean.groupby('cluster')[rating_col].mean().sort_values(ascending=False)
    
    cluster_mapping = {}
    labels = ["Pépites bien notées", "Profils Standards"]
    
    for i, cluster_id in enumerate(cluster_means.index):
        cluster_mapping[cluster_id] = labels[i] if i < len(labels) else f"Cluster {cluster_id}"

    df_clean['cluster_label'] = df_clean['cluster'].map(cluster_mapping)

    print(f" Clustering global terminé sur {len(df_clean)} restaurants.")

    # SAUVEGARDE DU MODÈLE EN .PKL
    os.makedirs("models", exist_ok=True)
    joblib.dump(kmeans, "models/kmeans_cluster_model.pkl")
    print(" Modèle K-Means sauvegardé dans 'models/kmeans_cluster_model.pkl'")

    return df_clean