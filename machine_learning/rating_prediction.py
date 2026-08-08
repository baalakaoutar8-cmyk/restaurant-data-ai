import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from machine_learning.preprocessing import clean_data_for_ml

def train_rating_model(df: pd.DataFrame):
    df_clean = clean_data_for_ml(df)
    
    df_model = df_clean[
        (df_clean['rating'].notna()) & 
        (df_clean['rating'] > 0)
    ].copy()
    
    if len(df_model) == 0:
        print(" Erreur : Aucun restaurant avec une note valide.")
        return None, {}

    print(f" Modèle entraîné sur {len(df_model)} restaurants avec des notes réelles.")

    df_model['log_reviews'] = np.log1p(df_model['reviews_count'].fillna(0))
    top_cities = df_model['city'].value_counts().head(10).index
    df_model['city_grouped'] = df_model['city'].apply(lambda c: c if c in top_cities else 'Autre')
    city_dummies = pd.get_dummies(df_model['city_grouped'], prefix='city', drop_first=True)

    X = pd.concat([
        df_model[['price_numeric', 'log_reviews', 'latitude', 'longitude']],
        city_dummies
    ], axis=1)
    
    y = df_model['rating']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        random_state=42
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    print(f" Metrics : MAE = {mae:.4f} | RMSE = {rmse:.4f} | R² = {r2:.4f}")

    # SAUVEGARDE DU MODÈLE EN .PKL
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/rating_prediction_model.pkl")
    print(" Modèle de prédiction sauvegardé dans 'models/rating_prediction_model.pkl'")

    return model, {"mae": mae, "rmse": rmse, "r2": r2}


def predict_missing_ratings(df: pd.DataFrame, model) -> pd.DataFrame:
    df_enriched = clean_data_for_ml(df)
    
    df_enriched['final_rating'] = df_enriched['rating']
    df_enriched['is_rating_estimated'] = False

    mask_missing = (df_enriched['rating'].isna()) | (df_enriched['rating'] == 0)
    
    if mask_missing.sum() > 0 and model is not None:
        df_missing = df_enriched[mask_missing].copy()
        
        df_missing['log_reviews'] = np.log1p(df_missing['reviews_count'].fillna(0))
        top_cities = df_enriched['city'].value_counts().head(10).index
        df_missing['city_grouped'] = df_missing['city'].apply(lambda c: c if c in top_cities else 'Autre')
        city_dummies = pd.get_dummies(df_missing['city_grouped'], prefix='city', drop_first=True)
        
        X_missing = pd.concat([
            df_missing[['price_numeric', 'log_reviews', 'latitude', 'longitude']],
            city_dummies
        ], axis=1)

        for col in model.feature_names_in_:
            if col not in X_missing.columns:
                X_missing[col] = 0
        X_missing = X_missing[model.feature_names_in_]

        predicted_values = model.predict(X_missing).round(2)
        
        df_enriched.loc[mask_missing, 'final_rating'] = predicted_values
        df_enriched.loc[mask_missing, 'is_rating_estimated'] = True

        print(f" Pseudo-labeling : {mask_missing.sum()} notes estimées par le modèle AI avec succès !")

    return df_enriched