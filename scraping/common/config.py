"""
Configuration commune du module de scraping.
Toutes les constantes utilisées par les différents scrapers sont définies ici.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ==========================================================
# Chargement des variables d'environnement
# ==========================================================

load_dotenv()

# ==========================================================
# Chemins du projet
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

LOGS_DIR = BASE_DIR / "logs"

RESOURCES_DIR = BASE_DIR / "resources"

COUNTRIES_DIR = RESOURCES_DIR / "countries"
CATEGORIES_DIR = RESOURCES_DIR / "categories"
PRIORITIES_DIR = RESOURCES_DIR / "priorities"

# Création automatique des dossiers

for folder in [
    RAW_DATA_DIR,
    INTERIM_DATA_DIR,
    PROCESSED_DATA_DIR,
    LOGS_DIR,
]:
    folder.mkdir(parents=True, exist_ok=True)

# ==========================================================
# API KEYS
# ==========================================================

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# ==========================================================
# Paramètres HTTP
# ==========================================================

REQUEST_TIMEOUT = 30

MAX_RETRIES = 5

RETRY_DELAY = 3

VERIFY_SSL = True

# ==========================================================
# User Agent
# ==========================================================

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/138.0 Safari/537.36"
)

# User-Agent pour les APIs qui le nécessitent
API_USER_AGENT = (
    "Restaurant-Data-AI/1.0 (+https://github.com/your-repo)"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "fr,en;q=0.9",
    "Accept": "application/json",
}

# ==========================================================
# Rate Limiting
# ==========================================================

MIN_DELAY = 2

MAX_DELAY = 5

MAX_REQUESTS_PER_MINUTE = 60

# ==========================================================
# Google Places
# ==========================================================

GOOGLE_PAGE_SIZE = 20

GOOGLE_LANGUAGE = "fr"

GOOGLE_REGION = "MA"

# ==========================================================
# Google Maps
# ==========================================================

SCROLL_PAUSE = 2

MAX_SCROLL = 50

# ==========================================================
# OpenStreetMap
# ==========================================================

OVERPASS_TIMEOUT = 60

# Using VK Maps (maps.mail.ru) Overpass instance instead of overpass-api.de
# which appears to be having issues with HTTP 406 responses.
# Both instances have global data coverage per OSM wiki.
# See: https://wiki.openstreetmap.org/wiki/Overpass_API#Public_Overpass_API_instances
OVERPASS_ENDPOINT = "https://maps.mail.ru/osm/tools/overpass/api/interpreter"

# Alternative endpoints (in case primary fails):
# - Main: https://overpass-api.de/api/interpreter (currently returning 406)
# - VK Maps: https://maps.mail.ru/osm/tools/overpass/api/interpreter (working)
# - Private Coffee: https://overpass.private.coffee/api/interpreter

# ==========================================================
# TripAdvisor
# ==========================================================

TRIPADVISOR_DELAY = 5

# ==========================================================
# TheFork
# ==========================================================

THEFORK_DELAY = 5

# ==========================================================
# Export
# ==========================================================

EXPORT_FORMAT = "csv"

CSV_ENCODING = "utf-8-sig"

# ==========================================================
# Logs
# ==========================================================

SCRAPING_LOG = LOGS_DIR / "scraping.log"

ERROR_LOG = LOGS_DIR / "errors.log"

# ==========================================================
# Progression
# ==========================================================

PROGRESS_FILE = LOGS_DIR / "progress.json"

# ==========================================================
# Colonnes standard de tous les scrapers
# ==========================================================

STANDARD_COLUMNS = [
    "source",
    "restaurant_id",
    "name",
    "country",
    "city",
    "district",
    "address",
    "latitude",
    "longitude",
    "phone",
    "website",
    "email",
    "opening_hours",
    "price_range",
    "cuisine_type",
    "services",
    "rating",
    "review_count",
    "photos",
    "google_maps_url",
    "scraped_at",
]

# ==========================================================
# Mode Debug
# ==========================================================

DEBUG = os.getenv("DEBUG", "False").lower() == "true"