"""
run_tripadvisor.py

Point d'entrée du scraper TripAdvisor.

Il suffit de modifier COUNTRY pour scraper un autre pays.
"""

from scraping.common.logger import get_logger
from scraping.tripadvisor.scraper import TripAdvisorScraper

logger = get_logger(__name__)

# =====================================================
# Choisir le pays à scraper
# =====================================================

COUNTRY = "kuwait"

# Exemples :
# COUNTRY = "saudi_arabia"
# COUNTRY = "uae"
# COUNTRY = "qatar"
# COUNTRY = "kuwait"
# COUNTRY = "bahrain"

# =====================================================
# Paramètres
# =====================================================

HEADLESS = False

# Limiter le nombre de villes (None = toutes)
MAX_CITIES = None

# Exemple :
# MAX_CITIES = 5

# =====================================================

def main():

    logger.info("=" * 70)
    logger.info("TripAdvisor Scraper")
    logger.info("=" * 70)

    scraper = TripAdvisorScraper(
        country=COUNTRY,
        headless=HEADLESS,
        max_cities=MAX_CITIES,
    )

    scraper.run()

    logger.info("Fin du scraping.")


if __name__ == "__main__":
    main()