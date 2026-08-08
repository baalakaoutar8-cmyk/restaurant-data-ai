import os
import json
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")

def extract_google_places() -> pd.DataFrame:
    """Extrait tous les fichiers JSON de Google Places."""
    gp_dir = RAW_DIR / "google_places"
    records = []
    
    if not gp_dir.exists():
        return pd.DataFrame()
        
    for file in gp_dir.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                items = data if isinstance(data, list) else data.get("results", [])
                for item in items:
                    item["source"] = "google_places"
                    records.append(item)
            except Exception as e:
                print(f"Erreur lors de la lecture de {file}: {e}")
                
    return pd.DataFrame(records)

def extract_openstreetmap() -> pd.DataFrame:
    """Extrait les fichiers CSV finalisés d'OpenStreetMap."""
    osm_dir = RAW_DIR / "openstreetmap"
    dfs = []
    
    if not osm_dir.exists():
        return pd.DataFrame()
        
    for file in osm_dir.rglob("*.csv"):
        try:
            df = pd.read_csv(file)
            df["source"] = "openstreetmap"
            dfs.append(df)
        except Exception as e:
            print(f"Erreur lors de la lecture de {file}: {e}")
            
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def extract_tripadvisor() -> pd.DataFrame:
    """Extrait les CSV/JSON de TripAdvisor."""
    ta_dir = RAW_DIR / "tripadvisor"
    dfs = []
    
    if not ta_dir.exists():
        return pd.DataFrame()
        
    for file in ta_dir.rglob("*.csv"):
        try:
            df = pd.read_csv(file)
            df["source"] = "tripadvisor"
            dfs.append(df)
        except Exception as e:
            print(f"Erreur lors de la lecture de {file}: {e}")
            
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def extract_all() -> dict:
    """Fonction principale d'extraction."""
    print("📥 Extraction des données brutes en cours...")
    return {
        "google_places": extract_google_places(),
        "openstreetmap": extract_openstreetmap(),
        "tripadvisor": extract_tripadvisor()
    }