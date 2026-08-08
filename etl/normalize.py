import pandas as pd  # type:ignore

COMMON_COLUMNS = [
    "name", "country", "city", "address", "latitude", "longitude",
    "phone", "website", "rating", "reviews_count", "price_range", "source"
]

def normalize_data(data_dict: dict) -> pd.DataFrame:
    """Harmonise le schéma de toutes les sources en un seul DataFrame unifié."""
    print("📐 Normalisation des schémas...")
    normalized_dfs = []
    
    for source, df in data_dict.items():
        if df.empty:
            continue
            
        norm_df = pd.DataFrame()
        
        # Mappage intelligent des colonnes selon la source
        norm_df["name"] = df.get("name") or df.get("title") or df.get("restaurant_name")
        norm_df["country"] = df.get("country") or df.get("country_name")
        norm_df["city"] = df.get("city") or df.get("town") or df.get("location_city")
        norm_df["address"] = df.get("address") or df.get("formatted_address") or df.get("street")
        norm_df["latitude"] = df.get("latitude") or df.get("lat")
        norm_df["longitude"] = df.get("longitude") or df.get("lng") or df.get("lon")
        norm_df["phone"] = df.get("phone") or df.get("international_phone_number")
        norm_df["website"] = df.get("website") or df.get("url")
        norm_df["rating"] = df.get("rating") or df.get("note")
        norm_df["reviews_count"] = df.get("reviews_count") or df.get("user_ratings_total") or 0
        norm_df["price_range"] = df.get("price_range") or df.get("price_level")
        norm_df["source"] = df.get("source", source)
        
        # Standardisation de la casse des noms
        if "name" in norm_df.columns:
            norm_df["name_clean"] = norm_df["name"].astype(str).str.lower().str.strip()
            
        normalized_dfs.append(norm_df)
        
    if not normalized_dfs:
        return pd.DataFrame(columns=COMMON_COLUMNS)
        
    full_df = pd.concat(normalized_dfs, ignore_index=True)
    return full_df