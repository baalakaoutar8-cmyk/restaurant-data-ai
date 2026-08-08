import pandas as pd
from sqlalchemy import create_engine, text

def save_predicted_ratings_to_db(df_enriched: pd.DataFrame, engine):
    """
    Met à jour la table PostgreSQL 'restaurants' avec les notes prédites.
    """
    # On isole uniquement les lignes où une note a été estimée
    df_to_update = df_enriched[df_enriched['is_rating_estimated'] == True][
        ['id', 'final_rating', 'is_rating_estimated']
    ].rename(columns={'final_rating': 'predicted_rating'})

    if df_to_update.empty:
        print("Aucune note prédite à enregistrer.")
        return

    print(f" Sauvegarde de {len(df_to_update)} notes prédites dans PostgreSQL...")

    # Utilisation d'une table temporaire SQL pour une mise à jour ultra-rapide (bulk update)
    with engine.begin() as conn:
        # 1. Création table temporaire
        df_to_update.to_sql('temp_ratings', conn, if_exists='replace', index=False)

        # 2. Exécution de la mise à jour (UPDATE JOIN)
        update_query = text("""
            UPDATE restaurants r
            SET 
                predicted_rating = t.predicted_rating,
                is_rating_estimated = t.is_rating_estimated
            FROM temp_ratings t
            WHERE r.id = t.id;
        """)
        conn.execute(update_query)

        # 3. Nettoyage de la table temporaire
        conn.execute(text("DROP TABLE temp_ratings;"))

    print(" Mise à jour réussie dans PostgreSQL !")