import sys
from pathlib import Path
from urllib.parse import quote_plus
import pandas as pd #type:ignore
from sqlalchemy import create_engine, text #type:ignore

# ==========================================
# 1. Configuration (Mot de passe fixé à '1234')
# ==========================================
DB_USER = "postgres"
DB_PASS = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "restaurants_db"

DATABASE_URL = f"postgresql+pg8000://{quote_plus(DB_USER)}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
EXPORT_DIR = Path("data/exports")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS restaurants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    city VARCHAR(100),
    address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    phone VARCHAR(100),
    website TEXT,
    rating DOUBLE PRECISION,
    reviews_count INT DEFAULT 0,
    price_range VARCHAR(50),
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_restaurant_location UNIQUE (name, country, city)
);
"""


def load_csv_to_postgres(file_path: Path):
    try:
        df = pd.read_csv(file_path, on_bad_lines="skip", encoding="utf-8-sig")
    except Exception:
        df = pd.read_csv(file_path, on_bad_lines="skip", encoding="utf-8")

    if df.empty:
        return

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["reviews_count"] = (
        pd.to_numeric(df["reviews_count"], errors="coerce").fillna(0).astype(int)
    )

    country_name = file_path.stem.replace("restaurants_", "").upper()

    try:
        df.to_sql("restaurants_temp", engine, if_exists="replace", index=False)

        upsert_query = """
        INSERT INTO restaurants (name, country, city, address, latitude, longitude, phone, website, rating, reviews_count, price_range, source)
        SELECT name, country, city, address, latitude, longitude, phone, website, rating, reviews_count, price_range, source
        FROM restaurants_temp
        ON CONFLICT (name, country, city) 
        DO UPDATE SET
            address = EXCLUDED.address,
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            phone = EXCLUDED.phone,
            website = EXCLUDED.website,
            rating = EXCLUDED.rating,
            reviews_count = EXCLUDED.reviews_count,
            source = EXCLUDED.source;
        
        DROP TABLE IF EXISTS restaurants_temp;
        """

        with engine.connect() as conn:
            conn.execute(text(upsert_query))
            conn.commit()

        print(f"  📥 {country_name} : {len(df)} lignes insérées.")
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion de {file_path.name} : {e}")


if __name__ == "__main__":
    print("🚀 Début du chargement ETL dans PostgreSQL...")

    try:
        with engine.connect() as conn:
            conn.execute(text(CREATE_TABLE_SQL))
            conn.commit()
        print("✅ Connexion réussie à 'restaurants_db' !")
    except Exception as err:
        print(f"❌ Connexion impossible : {err}")
        sys.exit(1)

    csv_files = list(EXPORT_DIR.glob("*.csv"))
    if not csv_files:
        print(f"⚠️ Aucun fichier CSV dans {EXPORT_DIR}")
    else:
        for file in csv_files:
            load_csv_to_postgres(file)
        print("\n🎉 Chargement terminé avec succès !")