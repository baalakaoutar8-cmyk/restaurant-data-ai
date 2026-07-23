"""
scraper.py

Contrôleur principal du scraping TripAdvisor.
"""

from __future__ import annotations

from scraping.common.logger import get_logger

from scraping.tripadvisor.browser import Browser
from scraping.tripadvisor.pipeline import Pipeline
from scraping.tripadvisor.storage import Storage
from scraping.tripadvisor.checkpoint import Checkpoint

from config.cities import (
    MOROCCO_CITIES,
    SAUDI_ARABIA_CITIES,
    UAE_CITIES,
    QATAR_CITIES,
    KUWAIT_CITIES,
    BAHRAIN_CITIES,
)

logger = get_logger(__name__)


class TripAdvisorScraper:

    COUNTRIES = {
        "morocco": MOROCCO_CITIES,
        "saudi_arabia": SAUDI_ARABIA_CITIES,
        "uae": UAE_CITIES,
        "qatar": QATAR_CITIES,
        "kuwait": KUWAIT_CITIES,
        "bahrain": BAHRAIN_CITIES,
    }

    def __init__(
        self,
        country: str,
        headless: bool = False,
        max_cities: int | None = None,
    ):

        self.country = country.lower()

        if self.country not in self.COUNTRIES:
            raise ValueError(f"Pays inconnu : {country}")

        self.cities = self.COUNTRIES[self.country]

        if max_cities is not None:
            self.cities = self.cities[:max_cities]

        self.browser = Browser(headless=headless)

        self.storage = Storage(self.country)

        self.checkpoint = Checkpoint()

    # ======================================================

    def run(self):

        logger.info("=" * 70)
        logger.info(
            "Début du scraping TripAdvisor (%s)",
            self.country
        )
        logger.info("=" * 70)

        page = self.browser.start()

        pipeline = Pipeline(page)

        # --------------------------------------------
        # Chargement du checkpoint
        # --------------------------------------------

        checkpoint = self.checkpoint.load()

        start_index = 0

        if (
            checkpoint
            and checkpoint["country"] == self.country
        ):
            start_index = checkpoint["city_index"] + 1

            logger.info(
                "Reprise à partir de la ville %s.",
                start_index
            )

        try:

            for index, city in enumerate(self.cities):

                if index < start_index:
                    continue

                logger.info("-" * 60)
                logger.info(
                    "[%s/%s] %s",
                    index + 1,
                    len(self.cities),
                    city
                )
                logger.info("-" * 60)

                try:

                    restaurants = pipeline.process_city(city)

                    self.storage.add(restaurants)

                    self.checkpoint.save(
                        self.country,
                        index
                    )

                except Exception as e:

                    logger.exception(
                        "Erreur sur %s : %s",
                        city,
                        e
                    )

            self.storage.save()

            self.checkpoint.clear()

            logger.info(
                "Scraping terminé."
            )

        finally:

            self.browser.stop()