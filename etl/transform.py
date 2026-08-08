import pandas as pd #type:ignore

def transform_data(df: pd.DataFrame) -> dict:
    """Mappe les données transformées vers le schéma relationnel cible."""
    print("⚙️ Transformation vers le schéma PostgreSQL...")
    if df.empty:
        return {"countries": pd.DataFrame(), "cities": pd.DataFrame(), "restaurants": pd.DataFrame()}
        
    # Table Pays
    countries_df = df[["country"]].dropna().drop_duplicates().rename(columns={"country": "country_name"})
    
    # Table Villes
    cities_df = df[["city", "country"]].dropna().drop_duplicates().rename(
        columns={"city": "city_name", "country": "country_name"}
    )
    
    # Table Restaurants
    restaurants_df = df[[
        "name", "address", "city", "country", "latitude", "longitude",
        "phone", "website", "price_range", "rating", "reviews_count", "source"
    ]].copy()
    
    restaurants_df = restaurants_df.rename(columns={
        "rating": "rating_score",
        "city": "city_name",
        "country": "country_name"
    })
    
    return {
        "countries": countries_df,
        "cities": cities_df,
        "restaurants": restaurants_df
    }