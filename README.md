# 🍽️ Restaurant Data AI — Plateforme d'Ingénierie de Données & Analytics Multi-Sources

Bienvenue dans le dépôt officiel du projet **Restaurant Data AI**.

Ce projet est une solution complète d'ingénierie de données (*Data Engineering*) et d'analyse décisionnelle. Il permet de scraper, nettoyer, structurer et analyser l'écosystème de la restauration à partir de multiples sources web et API (OpenStreetMap, Google Places, TripAdvisor). Les données sont consolidées dans une base relationnelle PostgreSQL pour alimenter des modèles de Machine Learning, des analyses de clustering spatial/commercial ainsi qu'une interface de visualisation dynamique via Streamlit.

---

## 📐 Architecture Technique du Pipeline

Le flux de traitement suit un pipeline ETL (*Extract, Transform, Load*) moderne structuré en 5 grands modules :

```text
  [ 1. SOURCES DE DONNÉES ]
     ├── OpenStreetMap (APIs Overpass)
     ├── Google Places API
     └── TripAdvisor Scraping
                │
                ▼
  [ 2. COLLECTE & SCRAPING ]
     ├── Scripting & requêtage automatisé
     └── Stockage temporaire des réponses brutes (JSON)
                │
                ▼
  [ 3. PIPELINE ETL & NETTOYAGE ]
     ├── Normalisation des schémas & formats
     ├── Dédoublonnage d'établissements multi-sources
     ├── Traitement des valeurs manquantes & géolocalisation
     └── Export & Structuration dans PostgreSQL (pgAdmin 4)
                │
                ▼
  [ 4. ANALYTICS & MACHINE LEARNING ]
     ├── Calcul des KPIs & Métriques d'activité
     ├── Clustering & Segmentation (Zonage, catégories)
     └── Modèles prédictifs 
                │
                ▼
  [ 5. RESTITUTION & VISUALISATION ]
     └── Dashboard Web interactif (Streamlit)
```

---

##  Organisation & Rôle Détaillé des Fichiers

| Catégorie | Fichier | Description & Rôle Technique |
| :--- | :--- | :--- |
| **Configuration** | `.env` | Stocke les variables d'environnement confidentielles (clés d'API, accès DB). |
| | `config.py` | Centralise les constantes, paramètres globaux et chemins de fichiers du projet. |
| | `.streamlit/config.toml` | Fichier de configuration visuelle pour personnaliser le Dashboard interactif Streamlit. |
| **Collecte & Data Scraping** | `demo_osm_scraper.py` | Extrait les nœuds et polygones géographiques (restaurants, cafés) via Overpass API (OSM). |
| | `run_google_places.py` | Interroge l'API Google Places pour récupérer les notes, nombre d'avis, adresses et niveaux de prix. |
| | `run_tripadvisor.py` | Moteur de scraping pour extraire les avis utilisateurs et détails spécifiques de TripAdvisor. |
| | `load_tripadvisor.py` | Charge et parse les structures brutes issues du scraping TripAdvisor. |
| **Pipeline ETL & Base de Données** | `data_preparation.py` | Cœur du nettoyage : dédoublonnage par similarité textuelle/spatiale, imputation et mise en forme. |
| | `load_to_postgres.py` | Gère les connexions SQL, la création des tables et le chargement des jeux de données nettoyés. |
| | `export_to_postgres.py` | Automatise l'exportation des métriques transformées et des vues statistiques vers PostgreSQL. |
| **Analyse & Modélisation ML** | `main_analysis.py` | Effectue les agrégations statistiques globales, calcul de moyennes et distribution par zones. |
| | `cluster_analysis.py` | Algorithmes de segmentation/clustering pour regrouper les restaurants par caractéristiques. |
| | `main_ml.py` | Scripts d'entraînement, de validation et d'évaluation des modèles de Machine Learning. |
| **Orchestration & Dashboard** | `main.py` | Script principal d'exécution orchestrant l'ensemble du pipeline et lançant l'interface. |


---

##  Configuration & Installation

### 1. Prérequis
* Python **3.13+**
* Une instance **PostgreSQL** active (administrable via pgAdmin 4)

### 2. Cloner le projet & Installer l'environnement
```bash
# 1. Clonez le dépôt GitHub
git clone <https://github.com/baalakaoutar8-cmyk/restaurant-data-ai.git>
cd restaurant-data-ai

# 2. Créez l'environnement virtuel
python -m venv .venv

# 3. Activez l'environnement virtuel
# Sur Linux / macOS :
source .venv/bin/activate
# Sur Windows :
.venv\Scripts\activate

# 4. Installez toutes les dépendances requises
pip install -r requirements.txt
```

### 3. Fichier de Configuration `.env`
Créez un fichier nommé `.env` à la racine du projet avec vos identifiants :

```env
# Configuration de la base de données PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=restaurant_db
DB_USER=votre_utilisateur
DB_PASSWORD=1234

# Clés d'API externes
GOOGLE_PLACES_API_KEY
GEMINI_API_key



### 2. Traitement multi-villes
Pour exécuter le pipeline de collecte et d'analyse à plus grande échelle sur plusieurs zones géographiques :
```bash
python run_[nom de modèle(tripadvisor, googleplace ou openstreetmap)].py
```

### 3. Lancer l'interface Web (Dashboard Streamlit)
Pour ouvrir le tableau de bord interactif dans votre navigateur :
```bash
python -m streamlit run dashboard/Home.py
```

---

##  Technologies & Stack Technique

* **Langage principal :** Python
* **Collecte de données :** Requests, BeautifulSoup4, Google Places API, Overpass API (OSM)
* **Traitement & Manipulation :** Pandas, NumPy
* **Base de données :** PostgreSQL, SQLAlchemy, `psycopg2`
* **Data Science & ML :** Scikit-Learn (Clustering & Modélisation)
* **Visualisation & UI :** Streamlit, Matplotlib, Seaborn