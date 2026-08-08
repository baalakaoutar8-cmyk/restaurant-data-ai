import re
import pandas as pd
from sqlalchemy import create_engine


def parse_tripadvisor_concatenated_row(text: str) -> dict:
  if not isinstance(text, str) or not text.strip():
    return {}

  extracted = {}

  # 1. Regex robuste découpant le bloc TripAdvisor complet
  # Group 1: Nom du restaurant (ex: Shanab Shawarma, KFC)
  # Group 2: Doublon éventuel du chiffre de la note (ex: 5.0 ou 2.2)
  # Group 3: Note réelle rating (ex: 5.0, 2.2, 4.04, 3.9)
  # Group 4: Nombre d'avis (ex: 2, 104, 6,501)
  # Group 5: Ville (ex: Seef, Manama, Dubai)
  # Group 6: Pays (ex: Bahrain, United Arab Emirates)
  pattern = (
      r"^(.*?)"  # Nom
      r"(?:(\d+\.\d+|\d+)\b)?\s*"  # Chiffre collé avant 'of 5 bubbles'
      r"(\d+(?:\.\d+)?)\s*of\s*5\s*bubbles\s*"  # Rating
      r"\(\s*([\d,]+)\s*reviews?\s*\)\s*"  # Reviews count
      r"([^,]+)?(?:,\s*([^0-9\n\r]+))?"  # Ville et Pays (s'arrête avant les chiffres de mentions)
  )

  match = re.search(pattern, text, re.IGNORECASE)

  if match:
    name, _, rating, reviews_count, city, country = match.groups()

    # Nettoyage Nom : enlève les préfixes et chiffres résiduels
    if name:
      clean_name = re.sub(r"^RESTAURANT\s*", "", name, flags=re.IGNORECASE)
      clean_name = re.sub(r"\d+(\.\d+)?\s*$", "", clean_name).strip()
      extracted["name"] = clean_name

    # Note
    if rating:
      try:
        val_rating = float(rating)
        if val_rating <= 5.0:
          extracted["rating"] = val_rating
      except ValueError:
        pass

    # Nombre d'avis
    if reviews_count:
      try:
        extracted["reviews_count"] = int(reviews_count.replace(",", ""))
      except ValueError:
        pass

    # Ville
    if city:
      extracted["city"] = city.strip()

    # Pays (nettoie la suite "3 mentions of...", etc.)
    if country:
      clean_country = re.sub(
          r"\d+\s*mentions?.*$", "", country, flags=re.IGNORECASE
      ).strip()
      # Enlever d'éventuels symboles d'étoiles ou texte collé
      clean_country = re.sub(r"[\"'\*].*$", "", clean_country).strip()
      extracted["country"] = clean_country

  return extracted


def clean_database():
  # 🔗 METTEZ VOTRE MOT DE PASSE POSTGRESQL ICI
  DB_URL = "postgresql://postgres:1234@localhost:5432/restaurants_db"

  print("🔌 Connexion à PostgreSQL...")
  engine = create_engine(DB_URL)

  df = pd.read_sql("SELECT * FROM restaurants", engine)
  print(f"📊 Nombre total de lignes chargées : {len(df)}")

  mask_corrupted = df["name"].astype(str).str.contains(
      r"of 5 bubbles", case=False, na=False
  )
  print(f"🔍 Nombre de lignes complexes à parser : {mask_corrupted.sum()}")

  for idx in df[mask_corrupted].index:
    raw_text = df.at[idx, "name"]
    parsed = parse_tripadvisor_concatenated_row(raw_text)

    for col, value in parsed.items():
      if col in df.columns:
        df.at[idx, col] = value

  print("💾 Sauvegarde de la base de données corrigée...")
  df.to_sql("restaurants", engine, if_exists="replace", index=False)
  print("✅ Nettoyage terminé avec succès !")


if __name__ == "__main__":
  clean_database()