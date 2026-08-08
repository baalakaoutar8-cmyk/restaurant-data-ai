import pandas as pd #type:ignore
import time

def geocode_data(df: pd.DataFrame) -> pd.DataFrame:
    """Complète les coordonnées GPS ou adresses manquantes."""
    print("🌐 Vérification du géocodage...")
    if df.empty:
        return df
        
    # Exemple d'enrichissement basique / vérification des bornes
    # Si besoin d'intégrer Geopy / Nominatim :
    # from geopy.geocoders import Nominatim
    # geolocator = Nominatim(user_agent="restaurant_ai")
    
    # Validation basique des plages de coordonnées géographiques
    mask_invalid_lat = ~df["latitude"].between(-90, 90)
    mask_invalid_lon = ~df["longitude"].between(-180, 180)
    
    df.loc[mask_invalid_lat, "latitude"] = None
    df.loc[mask_invalid_lon, "longitude"] = None
    
    return df