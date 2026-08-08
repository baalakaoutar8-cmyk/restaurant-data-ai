import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from machine_learning.preprocessing import clean_data_for_ml

def detect_suspicious_restaurants(df: pd.DataFrame) -> pd.DataFrame:
    df_clean = clean_data_for_ml(df)
    
    df_eval = df_clean[
        (df_clean['rating'].notna()) & 
        (df_clean['rating'] > 0)
    ].copy()

    if len(df_eval) == 0:
        df_clean['is_suspicious'] = False
        return df_clean

    df_eval['log_reviews'] = np.log1p(df_eval['reviews_count'].fillna(0))
    X = df_eval[['rating', 'log_reviews', 'price_numeric']]

    iso_forest = IsolationForest(
        contamination=0.03, 
        random_state=42
    )
    df_eval['anomaly_score'] = iso_forest.fit_predict(X)
    
    df_clean['is_suspicious'] = False
    suspicious_ids = df_eval[df_eval['anomaly_score'] == -1]['id']
    df_clean.loc[df_clean['id'].isin(suspicious_ids), 'is_suspicious'] = True

    print(f" Détection effectuée : {df_clean['is_suspicious'].sum()} restaurants suspects identifiés.")

    # SAUVEGARDE DU MODÈLE EN .PKL
    os.makedirs("models", exist_ok=True)
    joblib.dump(iso_forest, "models/isolation_forest_model.pkl")
    print(" Modèle Isolation Forest sauvegardé dans 'models/isolation_forest_model.pkl'")

    return df_clean