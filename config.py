"""
Configuration commune du module de scraping.
"""

from pathlib import Path

# ============================================================================
# CHEMINS
# ============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

INTERIM_DATA_DIR = DATA_DIR / "interim"

PROCESSED_DATA_DIR = DATA_DIR / "processed"

LOG_DIR = BASE_DIR / "logs"

RESOURCE_DIR = BASE_DIR / "resources"

COUNTRIES_DIR = RESOURCE_DIR / "countries"

PRIORITIES_DIR = RESOURCE_DIR / "priorities"

# Création automatique des dossiers

for directory in [
    DATA_DIR,
    RAW_DATA_DIR,
    INTERIM_DATA_DIR,
    PROCESSED_DATA_DIR,
    LOG_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# APIs
# ============================================================================

OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter"

NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/search"

# ============================================================================
# HTTP
# ============================================================================

USER_AGENT = (
    "RestaurantAIPlatform/1.0 "
    "(Educational Project; contact: your_email@example.com)"
)

REQUEST_TIMEOUT = 60

REQUEST_DELAY = 1.5

MAX_RETRIES = 3

RETRY_DELAY = 5

# ============================================================================
# SCRAPING
# ============================================================================

DEFAULT_COUNTRY = "Morocco"

EXPORT_FORMAT = "csv"

SAVE_AFTER_EACH_CITY = True

OVERPASS_TIMEOUT = 180

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = "INFO"

# ============================================================================
# OPENSTREETMAP
# ============================================================================

DEFAULT_OSM_TAGS = [
    ("amenity", "restaurant"),
    ("amenity", "fast_food"),
    ("amenity", "cafe"),
    ("amenity", "food_court"),
    ("amenity", "bar"),
    ("amenity", "pub"),
]
import os
from dotenv import load_dotenv


load_dotenv()


GOOGLE_PLACES_API_KEY = os.getenv(
    "GOOGLE_PLACES_API_KEY"
)