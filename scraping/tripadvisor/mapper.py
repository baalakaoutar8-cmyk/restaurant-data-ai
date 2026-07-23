"""
mapper.py

Transformation des données brutes TripAdvisor
vers le modèle commun du projet.
"""

from __future__ import annotations

from typing import Dict

from scraping.common.logger import get_logger

logger = get_logger(__name__)


class Mapper:
    """
    Transforme un restaurant brut vers
    le format standard du projet.
    """

    def map(self, restaurant: Dict) -> Dict:

        if restaurant is None:
            return {}

        return {

            "name": self._clean(restaurant.get("name")),

            "city": self._clean(restaurant.get("city")),

            "address": self._clean(restaurant.get("address")),

            "rating": self._to_float(
                restaurant.get("rating")
            ),

            "reviews_count": self._to_int(
                restaurant.get("reviews_count")
            ),

            "cuisine": self._clean(
                restaurant.get("cuisine")
            ),

            "price_range": self._clean(
                restaurant.get("price_range")
            ),

            "tripadvisor_url": self._clean(
                restaurant.get("tripadvisor_url")
            ),
        }

    # --------------------------------------------------

    @staticmethod
    def _clean(value):

        if value is None:
            return ""

        value = str(value).strip()

        return value

    # --------------------------------------------------

    @staticmethod
    def _to_float(value):

        if value is None:
            return None

        try:

            value = (
                str(value)
                .replace(",", ".")
            )

            return float(value)

        except Exception:

            return None

    # --------------------------------------------------

    @staticmethod
    def _to_int(value):

        if value is None:
            return 0

        try:

            digits = "".join(
                c for c in str(value)
                if c.isdigit()
            )

            if digits == "":
                return 0

            return int(digits)

        except Exception:

            return 0