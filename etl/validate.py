import pandas as pd # type:ignore

def validate_data(tables_dict: dict) -> bool:
    """Valide les règles métier et l'intégrité des données."""
    print("✅ Validation de la qualité des données...")
    
    restaurants = tables_dict.get("restaurants")
    
    if restaurants is None or restaurants.empty:
        print("⚠️ Attention : Aucun restaurant à valider.")
        return True
        
    # 1. Vérification : Le nom du restaurant est obligatoire
    invalid_names = restaurants["name"].isna().sum()
    if invalid_names > 0:
        print(f"❌ Erreur : {invalid_names} restaurants n'ont pas de nom.")
        return False
        
    # 2. Vérification : La note doit être comprise entre 1.0 et 5.0
    valid_ratings = restaurants["rating_score"].dropna().between(1.0, 5.0).all()
    if not valid_ratings:
        print("⚠️ Avertissement : Certaines notes dépassent l'intervalle [1, 5]. Elles seront corrigées.")
        restaurants.loc[restaurants["rating_score"] > 5.0, "rating_score"] = 5.0
        restaurants.loc[restaurants["rating_score"] < 1.0, "rating_score"] = 1.0

    print("   ➜ Toutes les règles de validation sont validées.")
    return True