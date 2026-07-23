"""
Gestion des villes à scraper.
"""

import json
from pathlib import Path

from scraping.common.config import (
    PRIORITIES_DIR,
    COUNTRIES_DIR,
)
from scraping.common.logger import get_logger

logger = get_logger(__name__)


class CityManager:
    """
    Gestionnaire des villes à scraper.

    - "uae" -> charge resources/priorities/uae.json
      (ce fichier contient un champ "priority" par ville)

    - tout autre pays -> charge resources/countries/<country>.json
      (ex : kuwait.json, qatar.json, uae.json, saudi_arabia.json,
      bahrain.json)
    """

    def __init__(self, country: str = "uae"):

        self.country = country
        self.country_key = self._normalize(country)

        self.filepath = self._resolve_filepath(self.country_key)

        self.cities = self.load()

    # ======================================================

    @staticmethod
    def _normalize(country: str) -> str:
        """
        Normalise le nom du pays pour construire le nom de fichier
        (ex : "uae" -> "uae").
        """

        return country.strip().lower().replace(" ", "_")

    # ======================================================

    def _resolve_filepath(self, country_key: str) -> Path:
        """
        Détermine le chemin du fichier JSON à charger
        en fonction du pays.
        """

        if country_key == "uae":
            return PRIORITIES_DIR / "uae.json"

        return COUNTRIES_DIR / f"{country_key}.json"

    # ======================================================

    def load(self):

        if not self.filepath.exists():

            raise FileNotFoundError(
                f"Fichier introuvable : {self.filepath}"
            )

        with open(
            self.filepath,
            encoding="utf-8",
        ) as f:

            data = json.load(f)

        logger.info(
            f"{len(data)} villes chargées pour {self.country}."
        )

        return data

    # ======================================================

    def get_all(self):
        return self.cities

    # ======================================================

    def get_by_priority(self, priority):
        """
        Retourne les villes correspondant à une priorité donnée.

        Si le fichier JSON du pays ne contient pas de champ
        "priority" (cas des pays autres que le Maroc), cette
        méthode retourne simplement une liste vide, sans erreur.
        """

        return [
            city
            for city in self.cities
            if city.get("priority") == priority
        ]

    # ======================================================

    def get_city(self, city_name):

        for city in self.cities:

            if city["city"].lower() == city_name.lower():

                return city

        return None

    # ======================================================

    def total(self):

        return len(self.cities)