import os
import pandas as pd
import urllib.parse
from sqlalchemy import create_engine, text

from machine_learning.rating_prediction import train_rating_model, predict_missing_ratings
from machine_learning.fake_review_detection import detect_suspicious_restaurants
from machine_learning.clustering import cluster_restaurants
from machine_learning.recommendation import recommend_restaurants

# Identifiants Database PostgreSQL
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")  # À adapter
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "restaurants_db")  # À adapter

password_encoded = urllib.parse.quote_plus(DB_PASSWORD)
DATABASE_URL = f"postgresql://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def save_ml_results_to_db(df_enriched: pd.DataFrame, engine):
    """
    Sauvegarde permanente de toutes les métriques ML dans PostgreSQL :
    - predicted_rating
    - is_rating_estimated
    - cluster_label
    - is_suspicious
    """
    cols_to_save = ['id', 'final_rating', 'is_rating_estimated', 'cluster_label', 'is_suspicious']
    df_to_update = df_enriched[cols_to_save].rename(columns={'final_rating': 'predicted_rating'})

    print(f" Sauvegarde de l'intégralité des résultats ML pour {len(df_to_update)} restaurants dans PostgreSQL...")

    with engine.begin() as conn:
        # Table temporaire
        df_to_update.to_sql('temp_ml_results', conn, if_exists='replace', index=False)

        # Mise à jour globale
        update_query = text("""
            UPDATE restaurants r
            SET 
                predicted_rating = t.predicted_rating,
                is_rating_estimated = t.is_rating_estimated,
                cluster_label = t.cluster_label,
                is_suspicious = t.is_suspicious
            FROM temp_ml_results t
            WHERE r.id = t.id;
        """)
        conn.execute(update_query)

        # Suppression table temporaire
        conn.execute(text("DROP TABLE temp_ml_results;"))

    print(" Mise à jour permanente dans la base PostgreSQL terminée avec succès !")


if __name__ == "__main__":
    print("==================================================")
    print("   DÉBUT DU PIPELINE Machine Learning & Sauvegardes")
    print("==================================================\n")
    
    engine = create_engine(DATABASE_URL)
    df_restaurants = pd.read_sql("SELECT * FROM restaurants;", engine)
    print(f" Dataset chargé depuis PostgreSQL : {len(df_restaurants)} restaurants au total.\n")

    # 1. Prédiction & Pseudo-Labeling
    print("--- 1. Entraînement & Estimation des Notes ---")
    model, metrics = train_rating_model(df_restaurants)
    df_enriched = predict_missing_ratings(df_restaurants, model)

    # 2. Détection d'Anomalies
    print("\n--- 2. Détection d'Anomalies (Faux Avis) ---")
    df_enriched = detect_suspicious_restaurants(df_enriched)

    # 3. Clustering
    print("\n--- 3. Clustering Global ---")
    df_enriched = cluster_restaurants(df_enriched)

    # 4. Sauvegarde dans PostgreSQL & Modèles .pkl
    print("\n--- 4. Sauvegarde Globale ---")
    save_ml_results_to_db(df_enriched, engine)

    # 5. Test Recommandation Hybride
    print("\n--- 5. Test Recommandation Hybride ---")
    print("\n Recommandations pour Casablanca :")
    recoms_casa = recommend_restaurants(df_enriched, city="Casablanca", country="Morocco", top_n=3)
    if not recoms_casa.empty:
        print(recoms_casa.to_string(index=False))

    print("\n==================================================")
    print("   TOUS LES MODÈLES (.pkl) ET RÉSULTATS (BDD) SONT SAUVEGARDÉS !")
    print("==================================================")