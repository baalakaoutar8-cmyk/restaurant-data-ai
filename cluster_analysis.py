import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Style des graphiques
sns.set_theme(style="whitegrid")

def run_kmeans_per_country():
    print("📂 Chargement des données préparées...")
    df_global = pd.read_csv("data_ready_for_ml.csv")
    
    # 1. Identifier les colonnes de pays créées par get_dummies (ex: 'country_MOROCCO')
    country_cols = [col for col in df_global.columns if col.startswith('country_')]
    
    if not country_cols:
        print("❌ Aucune colonne de pays trouvée dans le dataset.")
        return

    # Reconstituer le nom du pays sous forme de texte
    df_global['country_name'] = df_global[country_cols].idxmax(axis=1).str.replace('country_', '')

    countries = df_global['country_name'].unique()
    print(f"🌍 Pays détectés dans la base : {list(countries)}\n")

    features = ['rating', 'reviews_count', 'price_numeric', 'popularity_score']

    for country in countries:
        country_clean_name = country.lower().replace(" ", "_")
        
        # 2. Filtrer pour le pays courant et supprimer les valeurs manquantes sur les caractéristiques
        df_country = df_global[df_global['country_name'] == country].copy()
        df_country = df_country.dropna(subset=features)
        
        # Ne traiter que les pays ayant au moins 5 restaurants valides
        if len(df_country) < 5:
            print(f"⚠️ Ignoré : {country} n'a que {len(df_country)} restaurants valides.")
            continue

        print("="*60)
        print(f"📊 CLUSTERING EN COURS POUR : {country} ({len(df_country)} restaurants)")
        print("="*60)

        # 3. Sélection et Normalisation des données
        X = df_country[features].copy()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # 4. Détermination dynamique du nombre de clusters k (max 4)
        n_samples = len(df_country)
        k = min(4, n_samples)
        
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        df_country['cluster'] = kmeans.fit_predict(X_scaled)

        # 5. Affichage du résumé statistique par cluster
        cluster_summary = df_country.groupby('cluster')[features].agg(['count', 'mean']).round(2)
        print(cluster_summary)

        # 6. Génération et sauvegarde du graphique
        plt.figure(figsize=(10, 6))
        sns.scatterplot(
            data=df_country, 
            x='reviews_count', 
            y='rating', 
            hue='cluster', 
            palette='viridis', 
            alpha=0.8, 
            s=80
        )
        plt.xscale('log') # Échelle logarithmique pour le volume d'avis
        plt.title(f"Segmentation des Restaurants - {country} (Note vs Avis)", fontsize=14, fontweight='bold')
        plt.xlabel("Nombre d'avis (Échelle Log)")
        plt.ylabel("Note Moyenne (Rating)")
        plt.legend(title="Cluster")
        
        img_filename = f"kmeans_clusters_{country_clean_name}.png"
        plt.tight_layout()
        plt.savefig(img_filename)
        plt.close()

        # 7. Sauvegarde du fichier CSV nettoyé et segmenté
        df_country_to_save = df_country.drop(columns=['country_name'])
        csv_filename = f"data_clustered_{country_clean_name}.csv"
        df_country_to_save.to_csv(csv_filename, index=False)

        print(f" Graphique sauvegardé : {img_filename}")
        print(f" CSV sauvegardé       : {csv_filename}\n")

if __name__ == "__main__":
    run_kmeans_per_country()