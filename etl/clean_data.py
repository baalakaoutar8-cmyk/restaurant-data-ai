import pandas as pd # type:ignore
import numpy as np  # type:ignore

def clean_data(data_dict: dict) -> dict:
    """Nettoie et filtre les données brutes."""
    print("🧹 Nettoyage des données...")
    cleaned_dict = {}
    
    for source, df in data_dict.items():
        if df.empty:
            cleaned_dict[source] = df
            continue
            
        df = df.copy()
        
        # Suppression des doublons exacts de lignes
        df = df.drop_duplicates()
        
        # Nettoyage des colonnes texte si présentes
        for col in ["name", "address", "city", "country"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace(["nan", "None", "null", ""], np.nan)
        
        # Conversion numérique des notes et avis
        if "rating" in df.columns:
            df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
        if "reviews_count" in df.columns:
            df["reviews_count"] = pd.to_numeric(df["reviews_count"], errors="coerce").fillna(0).astype(int)
        if "latitude" in df.columns:
            df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
        if "longitude" in df.columns:
            df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
            
        cleaned_dict[source] = df
        
    return cleaned_dict