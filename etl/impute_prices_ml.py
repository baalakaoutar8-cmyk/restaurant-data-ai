import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import OrdinalEncoder
from sqlalchemy import create_engine


def impute_prices_with_ml():
  # 🔗 Remplacer VOTRE_MOT_DE_PASSE
  DB_URL = "postgresql://postgres:1234@localhost:5432/restaurants_db"
  print("🔌 Connexion à PostgreSQL...")
  engine = create_engine(DB_URL)

  df = pd.read_sql("SELECT * FROM restaurants", engine)
  print(f"📊 Données chargées : {len(df)} lignes.")

  # 1. Sélection et préparation des features pour le modèle ML
  features = ["country", "city", "cuisine", "rating", "reviews_count"]

  df_ml = df[features].copy()

  # Remplacer les Nones/NaNs par 'Inconnu' pour les catégorielles
  for col in ["country", "city", "cuisine"]:
    df_ml[col] = df_ml[col].fillna("Unknown").astype(str)

  # Imputation simple par la médiane pour les métriques numériques de base si manquantes
  df_ml["rating"] = df_ml["rating"].fillna(df_ml["rating"].median())
  df_ml["reviews_count"] = df_ml["reviews_count"].fillna(0)

  # 2. Encodage Ordinal pour transformer les textes en valeurs numériques pour le ML
  encoder = OrdinalEncoder(
      handle_unknown="use_encoded_value", unknown_value=-1
  )
  df_encoded = pd.DataFrame(
      encoder.fit_transform(df_ml[["country", "city", "cuisine"]]),
      columns=["country_enc", "city_enc", "cuisine_enc"],
  )

  df_encoded["rating"] = df_ml["rating"].values
  df_encoded["reviews_count"] = df_ml["reviews_count"].values
  df_encoded["avg_price"] = df["avg_price"].values  # Contient des NaNs

  # 3. Entraînement du modèle d'imputation IterativeImputer (Random Forest)
  print("🤖 Entraînement du modèle Machine Learning d'imputation...")
  imputer = IterativeImputer(
      estimator=RandomForestRegressor(n_estimators=50, random_state=42),
      max_iter=10,
      random_state=42,
  )

  imputed_array = imputer.fit_transform(df_encoded)

  # 4. Récupération des prix prédits/imputés (dernière colonne)
  predicted_prices = imputed_array[:, -1]

  # S'assurer que les prix sont réalistes (> 0) et arrondis
  df["avg_price"] = np.round(np.clip(predicted_prices, a_min=30.0, a_max=800.0), 2)

  print("💾 Sauvegarde des prix prédits dans PostgreSQL...")
  df.to_sql("restaurants", engine, if_exists="replace", index=False)
  print("✅ Imputation par Machine Learning terminée avec succès !")


if __name__ == "__main__":
  impute_prices_with_ml()