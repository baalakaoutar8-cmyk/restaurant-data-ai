"""
Script d'exécution principal pour le scraper TripAdvisor.
"""

import sys
import logging
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright #type:ignore

from scraping.common.logger import get_logger
from scraping.tripadvisor.pipeline import Pipeline
from scraping.tripadvisor.storage import Storage

logger = get_logger("run_tripadvisor")

# 🎯 Définissez le pays et la/les villes associées
COUNTRY_NAME = "kuwait"
TARGET_CITIES = [
    "Kuwait City",
]


def clean_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filtre les faux éléments récupérés lors du scraping
    (ex: les liens d'avis nommés '(244 reviews)').
    """
    cleaned = []
    for item in results:
        name = item.get("name", "") or item.get("title", "")
        # Ignorer les éléments vides ou qui contiennent uniquement le texte de reviews
        if not name or "reviews" in name.lower() or "avis" in name.lower():
            continue
        cleaned.append(item)
    return cleaned


def run() -> None:
    logger.info("Démarrage du scraper TripAdvisor...")

    # Instanciation de votre Storage avec le nom du pays
    storage = Storage(country=COUNTRY_NAME)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
            locale="fr-FR"
        )

        page = context.new_page()
        pipeline = Pipeline(page)

        for city in TARGET_CITIES:
            try:
                logger.info("Traitement de la ville : %s", city)
                raw_restaurants = pipeline.process_city(city)

                if raw_restaurants:
                    # Nettoyage des éléments parasites (ex: '(244 reviews)')
                    valid_restaurants = clean_results(raw_restaurants)
                    logger.info("✔ %d restaurants valides récupérés pour %s", len(valid_restaurants), city)
                    
                    # Ajout dans l'accumulateur Storage
                    storage.add(valid_restaurants)
                else:
                    logger.warning("⚠ Aucun restaurant récupéré pour %s", city)

            except Exception as exc:
                logger.error("Erreur critique sur la ville %s : %s", city, exc, exc_info=True)

        browser.close()

    # Sauvegarde finale dans data/tripadvisor/{country}.csv
    logger.info("Sauvegarde finale des données...")
    storage.save()
    logger.info("Processus terminé avec succès !")


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)