"""
validator.py

Validation des restaurants extraits depuis TripAdvisor.
"""

from __future__ import annotations

from typing import Dict

from scraping.common.logger import get_logger

logger = get_logger(__name__)


class Validator:
    """
    Valide les données d'un restaurant.
    """

    def is_valid(self, restaurant: Dict) -> bool:
        """
        Vérifie qu'un restaurant contient les
        informations minimales.
        """

        if not restaurant:

            logger.debug("Restaurant vide.")

            return False

        # -------------------------
        # Nom obligatoire
        # -------------------------

        name = restaurant.get("name", "").strip()

        if not name:

            logger.debug("Restaurant ignoré : nom absent.")

            return False

        # -------------------------
        # Ville obligatoire
        # -------------------------

        city = restaurant.get("city", "").strip()

        if not city:

            logger.debug(
                "Restaurant '%s' ignoré : ville absente.",
                name
            )

            return False

        # -------------------------
        # URL TripAdvisor
        # -------------------------

        url = restaurant.get("tripadvisor_url", "").strip()

        if url and not url.startswith("http"):

            logger.debug(
                "Restaurant '%s' ignoré : URL invalide.",
                name
            )

            return False

        # -------------------------
        # Rating
        # -------------------------

        rating = restaurant.get("rating")

        if rating is not None:

            try:

                rating = float(rating)

                if rating < 0 or rating > 5:

                    logger.debug(
                        "Restaurant '%s' ignoré : note invalide.",
                        name
                    )

                    return False

            except Exception:

                logger.debug(
                    "Restaurant '%s' ignoré : note invalide.",
                    name
                )

                return False

        # -------------------------
        # Nombre d'avis
        # -------------------------

        reviews = restaurant.get("reviews_count")

        if reviews is not None:

            try:

                reviews = int(reviews)

                if reviews < 0:

                    return False

            except Exception:

                return False

        logger.debug(
            "Restaurant valide : %s",
            name
        )

        return True