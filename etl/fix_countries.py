import pandas as pd
from sqlalchemy import create_engine

# Importation directe de tes listes depuis config/cities.py
from config.cities import (
    BAHRAIN_CITIES,
    KUWAIT_CITIES,
    MOROCCO_CITIES,
    QATAR_CITIES,
    SAUDI_ARABIA_CITIES,
    UAE_CITIES,
)

# Construction du dictionnaire de correspondance
CITIES_BY_COUNTRY = {
    'MOROCCO': MOROCCO_CITIES,
    'Saudi Arabia': SAUDI_ARABIA_CITIES,
    'United Arab Emirates': UAE_CITIES,
    'Qatar': QATAR_CITIES,
    'Kuwait': KUWAIT_CITIES,
    'Bahrain': BAHRAIN_CITIES,
}


def map_country_from_city(city_name: str, current_country: str) -> str:
  if not isinstance(city_name, str) or not city_name.strip():
    return current_country

  city_lower = city_name.strip().lower()

  # Recherche de la ville dans les listes des pays
  for country, cities in CITIES_BY_COUNTRY.items():
    if any(c.lower() == city_lower for c in cities):
      return country

  # Si la ville n'est pas trouvée, on conserve le pays actuel
  return current_country


def fix_countries_in_db():
  # 🔗 Pense à mettre ton mot de passe PostgreSQL
  DB_URL = "postgresql://postgres:1234@localhost:5432/restaurants_db"

  print("🔌 Connexion à PostgreSQL...")
  engine = create_engine(DB_URL)

  df = pd.read_sql("SELECT * FROM restaurants", engine)
  print(f"📊 Traitement de {len(df)} lignes...")

  # Application du re-mapping
  df["country"] = df.apply(
      lambda row: map_country_from_city(row["city"], row["country"]), axis=1
  )

  print("💾 Sauvegarde des pays corrigés dans PostgreSQL...")
  df.to_sql("restaurants", engine, if_exists="replace", index=False)
  print("✅ Le re-mapping des pays s'est terminé avec succès !")


if __name__ == "__main__":
  fix_countries_in_db()