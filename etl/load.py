import pandas as pd #type:ignore
from sqlalchemy import create_engine, text #type:ignore

# Configuration PostgreSQL (À adapter selon votre installation pgAdmin 4)
DB_USER = "postgres"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "restaurant_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_engine():
    return create_engine(DATABASE_URL)

def load_data(tables_dict: dict):
    """Insère les données nettoyées dans la base PostgreSQL."""
    print("🐘 Connexion et chargement des données dans PostgreSQL...")
    engine = get_engine()
    
    with engine.begin() as conn:
        # 1. Insertion des Pays
        countries_df = tables_dict["countries"]
        for country in countries_df["country_name"].unique():
            conn.execute(
                text("INSERT INTO countries (country_name) VALUES (:c) ON CONFLICT (country_name) DO NOTHING;"),
                {"c": country}
            )
            
        # 2. Insertion des Villes
        cities_df = tables_dict["cities"]
        for _, row in cities_df.iterrows():
            conn.execute(
                text("""
                    INSERT INTO cities (city_name, country_id)
                    SELECT :city, country_id FROM countries WHERE country_name = :country
                    ON CONFLICT (city_name, country_id) DO NOTHING;
                """),
                {"city": row["city_name"], "country": row["country_name"]}
            )
            
        # 3. Insertion des Restaurants
        restaurants_df = tables_dict["restaurants"]
        for _, row in restaurants_df.iterrows():
            conn.execute(
                text("""
                    INSERT INTO restaurants (
                        name, address, city_id, latitude, longitude,
                        phone, website, price_range, rating_score, reviews_count, source
                    )
                    VALUES (
                        :name, :address,
                        (SELECT city_id FROM cities c JOIN countries co ON c.country_id = co.country_id 
                         WHERE c.city_name = :city AND co.country_name = :country LIMIT 1),
                        :lat, :lon, :phone, :website, :price, :rating, :reviews, :source
                    );
                """),
                {
                    "name": row["name"],
                    "address": row.get("address"),
                    "city": row.get("city_name"),
                    "country": row.get("country_name"),
                    "lat": row.get("latitude"),
                    "lon": row.get("longitude"),
                    "phone": row.get("phone"),
                    "website": row.get("website"),
                    "price": row.get("price_range"),
                    "rating": row.get("rating_score"),
                    "reviews": row.get("reviews_count", 0),
                    "source": row.get("source")
                }
            )

    print("🎉 Insertion dans PostgreSQL effectuée avec succès !")