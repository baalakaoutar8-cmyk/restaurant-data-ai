import os
import glob
import pandas as pd #type:ignore
import psycopg2 #type:ignore

DB_CONFIG = {
    "dbname": "restaurants_db",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432"
}

TRIPADVISOR_DIR = os.path.join("data", "tripadvisor")

def safe_str(val, limit=255):
    """Convertit en chaîne, nettoie et tronque à la limite spécifiée."""
    if pd.notna(val) and val is not None:
        s = str(val).strip()
        return s[:limit] if s else None
    return None

def load_tripadvisor_data():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    csv_files = glob.glob(os.path.join(TRIPADVISOR_DIR, "*.csv"))
    
    insert_query = """
    INSERT INTO restaurants (
        name, country, city, address, latitude, longitude, phone, website, rating, reviews_count, price_range, source
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'tripadvisor')
    ON CONFLICT (name, country, city) 
    DO UPDATE SET 
        rating = COALESCE(EXCLUDED.rating, restaurants.rating),
        reviews_count = COALESCE(EXCLUDED.reviews_count, restaurants.reviews_count),
        phone = COALESCE(EXCLUDED.phone, restaurants.phone),
        website = COALESCE(EXCLUDED.website, restaurants.website),
        price_range = COALESCE(EXCLUDED.price_range, restaurants.price_range),
        source = CASE 
            WHEN restaurants.source NOT LIKE '%%tripadvisor%%' THEN restaurants.source || ', tripadvisor'
            ELSE restaurants.source 
        END;
    """

    for file in csv_files:
        country_name = os.path.basename(file).replace(".csv", "").upper().replace("_", " ")
        print(f"Chargement de {file} pour le pays: {country_name}...")
        
        df = pd.read_csv(file)
        
        for _, row in df.iterrows():
            # Application de la troncature sécurisée
            name = safe_str(row.get('name'))
            city = safe_str(row.get('city'))
            address = safe_str(row.get('address'))
            phone = safe_str(row.get('phone'))
            website = safe_str(row.get('website'))
            price_range = safe_str(row.get('price_range'))

            # Traitement des valeurs numériques
            lat = float(row.get('latitude')) if pd.notna(row.get('latitude')) else None
            lon = float(row.get('longitude')) if pd.notna(row.get('longitude')) else None
            rating = float(row.get('rating')) if pd.notna(row.get('rating')) else None
            
            try:
                reviews_count = int(row.get('reviews_count')) if pd.notna(row.get('reviews_count')) else 0
            except (ValueError, TypeError):
                reviews_count = 0

            # Sauter la ligne si le nom du restaurant est vide
            if not name:
                continue

            cursor.execute(insert_query, (
                name,
                country_name,
                city,
                address,
                lat,
                lon,
                phone,
                website,
                rating,
                reviews_count,
                price_range
            ))

    conn.commit()
    cursor.close()
    conn.close()
    print("\n Importation de toutes les données TripAdvisor terminée avec succès !")

if __name__ == "__main__":
    load_tripadvisor_data()