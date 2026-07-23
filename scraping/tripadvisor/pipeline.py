"""
pipeline.py

Pipeline principal du scraping TripAdvisor.
"""

from __future__ import annotations

from typing import List, Dict, Any

from scraping.common.logger import get_logger

from scraping.tripadvisor.search import Search
from scraping.tripadvisor.parser import TripAdvisorParser
from scraping.tripadvisor.mapper import Mapper
from scraping.tripadvisor.validator import Validator

logger = get_logger(__name__)


class Pipeline:
    """
    Pipeline de traitement d'une ville.

    Recherche
        ↓
    Extraction
        ↓
    Mapping
        ↓
    Validation
    """

    def __init__(self, page):
        self._page = page          # stocke la page Playwright
        self.search = Search(page)
        self.mapper = Mapper()
        self.validator = Validator()

    def process_city(self, city: str) -> List[Dict[str, Any]]:
        """
        Traite une ville complète.

        Retourne la liste des restaurants valides.
        """

        logger.info("=" * 60)
        logger.info("Ville : %s", city)
        logger.info("=" * 60)

        # --------------------------------------------------
        # 1. Recherche
        # --------------------------------------------------

        if not self.search.search(city):
            logger.warning(
                "Impossible de trouver la ville : %s",
                city
            )
            return []

        # --------------------------------------------------
        # 2. Extraction
        # --------------------------------------------------

        parser = TripAdvisorParser(self._page, city_name=city)
        raw_restaurants = parser.parse_page_deduplicated()

        logger.info(
            "%s restaurants extraits",
            len(raw_restaurants)
        )

        # --------------------------------------------------
        # 3. Mapping + Validation
        # --------------------------------------------------

        restaurants = []

        for raw in raw_restaurants:
            try:
                # Convertir en dict selon le type de 'raw'
                if isinstance(raw, dict):
                    raw_dict = raw
                elif hasattr(raw, "to_dict"):
                    raw_dict = raw.to_dict()
                else:
                    raw_dict = dict(raw)

                # Mapping vers la structure finale
                restaurant = self.mapper.map(raw_dict)

                # Validation des données
                if self.validator.is_valid(restaurant):
                    restaurants.append(restaurant)

            except Exception as e:
                logger.exception("Erreur lors du traitement du restaurant : %s", e)

        logger.info(
            "%s restaurants valides",
            len(restaurants)
        )

        return restaurants