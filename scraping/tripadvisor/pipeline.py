"""
Pipeline principal du scraping TripAdvisor.

Recherche des listings -> Extraction de chaque page détaillée -> Mapping -> Validation.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from scraping.common.logger import get_logger
from scraping.tripadvisor.mapper import Mapper
from scraping.tripadvisor.parser import TripAdvisorParser
from scraping.tripadvisor.search import Search
from scraping.tripadvisor.validator import Validator

logger = get_logger(__name__)


class Pipeline:
    """Pipeline de traitement d'une ville."""

    def __init__(self, page: Any) -> None:
        self._page = page
        self.search = Search(page)
        self.mapper = Mapper()
        self.validator = Validator()

    def process_city(self, city: str) -> List[Dict[str, Any]]:
        """Traite une ville complète."""
        logger.info("=" * 60)
        logger.info("Ville : %s", city)
        logger.info("=" * 60)

        # 1. Recherche
        if not self.search.search(city):
            logger.warning("Impossible de trouver la ville : %s", city)
            return []

        # Enregistrement d'une capture d'écran pour débogage visuel
        try:
            self._page.screenshot(path=f"debug_{city.replace(' ', '_')}.png")
            logger.debug("Capture d'écran de débogage enregistrée pour %s", city)
        except Exception as e:
            logger.warning("Impossible de créer la capture d'écran : %s", e)

        # 2. Extraction Phase 1 (Listing & URLs)
        parser = TripAdvisorParser(self._page, city_name=city)
        raw_restaurants_preview = parser.parse_page_deduplicated()

        logger.info("%d restaurants trouvés dans la liste pour %s", len(raw_restaurants_preview), city)

        # 3. Extraction Phase 2 (Détail de chaque restaurant)
        detailed_restaurants: List[Dict[str, Any]] = []

        for idx, preview in enumerate(raw_restaurants_preview, 1):
            detail_url = preview.get("url") or preview.get("tripadvisor_url")
            if not detail_url:
                logger.warning("[%d/%d] Aucune URL valide trouvée pour %s", idx, len(raw_restaurants_preview), preview.get("name"))
                detailed_restaurants.append(preview)
                continue

            try:
                logger.info("[%d/%d] Scraping détail : %s", idx, len(raw_restaurants_preview), preview.get("name", "Restaurant"))
                
                self._page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(1.5)

                detail_parser = TripAdvisorParser(self._page, city_name=city)
                
                if hasattr(detail_parser, "parse_detail"):
                    full_details = detail_parser.parse_detail(city_name=city)
                else:
                    full_details = {}

                combined_data = {**preview, **full_details}
                detailed_restaurants.append(combined_data)

            except Exception as exc:
                logger.error("Erreur lors de la navigation vers la page détail %s : %s", detail_url, exc)
                detailed_restaurants.append(preview)

        # 4. Mapping + Validation
        valid_restaurants: List[Dict[str, Any]] = []

        for raw in detailed_restaurants:
            try:
                if isinstance(raw, dict):
                    raw_dict = raw
                elif hasattr(raw, "to_dict"):
                    raw_dict = raw.to_dict()
                else:
                    raw_dict = dict(raw)

                restaurant = self.mapper.map(raw_dict)

                if self.validator.is_valid(restaurant):
                    valid_restaurants.append(restaurant)
                else:
                    logger.warning("Restaurant invalide rejeté : %s", raw_dict.get("name"))

            except Exception as e:
                logger.exception("Erreur lors du traitement du restaurant : %s", e)

        logger.info("=" * 60)
        logger.info("%d / %d restaurants validés avec succès pour %s", len(valid_restaurants), len(detailed_restaurants), city)
        logger.info("=" * 60)

        return valid_restaurants