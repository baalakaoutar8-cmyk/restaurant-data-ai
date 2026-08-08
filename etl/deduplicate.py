import pandas as pd

def deduplicate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les doublons cross-sources."""
    print("🔍 Détection et suppression des doublons...")
    if df.empty:
        return df
        
    initial_count = len(df)
    
    # 1. Règle principale : Même nom nettoyé + même ville
    df_dedup = df.drop_duplicates(subset=["name_clean", "city"], keep="first").copy()
    
    # 2. Règle secondaire : Si latitude/longitude identiques
    df_dedup = df_dedup.drop_duplicates(subset=["latitude", "longitude"], keep="first")
    
    # Nettoyage de la colonne temporaire
    if "name_clean" in df_dedup.columns:
        df_dedup = df_dedup.drop(columns=["name_clean"])
        
    final_count = len(df_dedup)
    print(f"   ➜ {initial_count - final_count} doublons supprimés ({final_count} restaurants uniques).")
    
    return df_dedup