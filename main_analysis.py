import os
import pandas as pd
from sqlalchemy import create_engine

# Configuration des imports du dossier analysis
from analysis.statistics import get_rating_price_correlation, top_rated_cities, cuisine_popularity
from analysis.kpi import compute_global_kpis
from analysis.visualization import plot_rating_vs_price, plot_geographic_distribution
from analysis.reports import generate_summary_report

# ==========================================
# 1. PARAMÈTRES DE CONNEXION POSTGRESQL
# ==========================================
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")  # <-- Remplacez ici
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "restaurants_db")        # <-- Remplacez ici

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def load_data_from_postgres():
    """Charge la table restaurants depuis PostgreSQL."""
    try:
        engine = create_engine(DATABASE_URL)
        print(" Connexion à PostgreSQL réussie.")
        
        # Requête sur la table 'restaurants'
        query_restaurants = "SELECT * FROM restaurants;"
        df_restaurants = pd.read_sql(query_restaurants, engine)
        
        # Table des avis individuels (passée à None pour le moment si pas encore créée)
        df_reviews = None  
        
        print(f" Dataframe Restaurants chargé : {df_restaurants.shape[0]} lignes.")
        return df_restaurants, df_reviews
        
    except Exception as e:
        print(f" Erreur lors de la connexion/lecture PostgreSQL : {e}")
        return None, None

# ==========================================
# 2. EXÉCUTION DU TEST GLOBALE
# ==========================================
def main():
    print("=== DÉBUT DU TEST DU MODULE ANALYSIS ===")
    
    # Étape A: Chargement
    df_restaurants, df_reviews = load_data_from_postgres()
    
    if df_restaurants is None or df_restaurants.empty:
        print(" Arrêt : Aucune donnée chargée.")
        return

    # Étape B: KPIs
    print("\n--- 1. Indicateurs KPIs (kpi.py) ---")
    kpis = compute_global_kpis(df_restaurants, df_reviews)
    for key, value in kpis.items():
        print(f"  • {key}: {value}")

    # Étape C: Statistiques
    print("\n--- 2. Analyses Statistiques (statistics.py) ---")
    corr = get_rating_price_correlation(df_restaurants)
    print(f"  • Corrélation Prix vs Note : {corr:.4f}")
    
    print("\n Top Villes les mieux notées :")
    print(top_rated_cities(df_restaurants).head())
    
    if 'cuisine' in df_restaurants.columns:
        print("\n Cuisines populaires :")
        print(cuisine_popularity(df_restaurants).head())

    # Étape D: Visualisations
    print("\n--- 3. Generation des Graphiques (visualization.py) ---")
    fig_price = plot_rating_vs_price(df_restaurants)
    fig_map = plot_geographic_distribution(df_restaurants)
    print(" Figures Plotly générées en mémoire avec succès.")

    # Étape E: Export du Rapport
    print("\n--- 4. Export du Rapport (reports.py) ---")
    df_report = generate_summary_report(df_restaurants, output_path="exports/summary_report.csv")
    print(f" Rapport récapitulatif généré ({df_report.shape[0]} lignes).")

    print("\n=== TEST DE ANALYSIS TERMINÉ AVEC SUCCÈS ===")

if __name__ == "__main__":
    main()