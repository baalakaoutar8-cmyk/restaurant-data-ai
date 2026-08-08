import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import urllib.parse
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

sns.set_theme(style="whitegrid")

def load_data_from_postgres():
    """ Connexion sécurisée à PostgreSQL """
    USER = "postgres"
    PASSWORD = "1234"  # ⚠️ REMPLACEZ PAR VOTRE MOT DE PASSE PGADMIN
    HOST = "localhost"
    PORT = "5432"
    DB_NAME = "restaurants_db"
    
    safe_password = urllib.parse.quote_plus(PASSWORD)
    safe_user = urllib.parse.quote_plus(USER)
    
    connection_string = f"postgresql://{safe_user}:{safe_password}@{HOST}:{PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    print("🔌 Connexion à la base PostgreSQL...")
    query = "SELECT * FROM restaurants_ready_for_ml;"
    df = pd.read_sql(query, engine)
    print(f" Datasets extrait avec succès : {len(df)} lignes.\n")
    return df

def train_rating_model_per_country():
    df_global = load_data_from_postgres()
    
    # Reconstituer le nom du pays à partir des colonnes One-Hot (ex: country_MOROCCO)
    country_cols = [col for col in df_global.columns if col.startswith('country_')]
    if country_cols:
        df_global['country_name'] = df_global[country_cols].idxmax(axis=1).str.replace('country_', '')
    else:
        print("❌ Colonnes de pays non trouvées.")
        return

    countries = df_global['country_name'].unique()
    
    # Les caractéristiques réelles (hors variable pays)
    candidate_features = ['reviews_count', 'price_numeric', 'popularity_score', 'images_count', 'is_open']
    features = [col for col in candidate_features if col in df_global.columns]
    
    print(f"🎯 Variables explicatives utilisées pour prédire la note : {features}\n")

    for country in countries:
        country_clean = country.lower().replace(" ", "_")
        
        # Filtrage par pays
        df_country = df_global[df_global['country_name'] == country].copy()
        df_country = df_country.dropna(subset=['rating'] + features)
        
        # Vérification qu'il y a assez de données
        if len(df_country) < 15:
            print(f"⚠️ Ignoré : {country} n'a que {len(df_country)} restaurants (insuffisant pour du ML).")
            continue

        print("="*60)
        print(f"🌲 PRÉDICTION ET ENTRAÎNEMENT POUR : {country} ({len(df_country)} restaurants)")
        print("="*60)

        X = df_country[features]
        y = df_country['rating']

        # 1. Découpage Train/Test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 2. Entraînement Random Forest
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)

        # 3. Prédictions & Évaluation
        y_pred = rf_model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        print(f"• Erreur Absolue Moyenne (MAE) : {mae:.3f}")
        print(f"• Erreur Quadratique (RMSE)    : {rmse:.3f}")
        print(f"• Score R² (Explicabilité)    : {r2:.3f}")

        # 4. Importance des variables pour ce pays
        importances = pd.Series(rf_model.feature_importances_, index=features).sort_values(ascending=False)
        
        plt.figure(figsize=(8, 4))
        sns.barplot(x=importances.values, y=importances.index, palette="mako")
        plt.title(f"Importance des Variables ({country})", fontsize=13, fontweight='bold')
        plt.xlabel("Importance (Poids)")
        
        img_filename = f"feature_importance_{country_clean}.png"
        plt.tight_layout()
        plt.savefig(img_filename)
        plt.close()

        print(f" Graphique sauvegardé : {img_filename}\n")

if __name__ == "__main__":
    train_rating_model_per_country()