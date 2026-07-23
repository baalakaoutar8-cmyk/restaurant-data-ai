"""
Gestion de la progression du scraping.
"""

import json

from scraping.common.config import PROGRESS_FILE
from scraping.common.logger import get_logger

logger = get_logger(__name__)


class ProgressManager:

    def __init__(self):

        if not PROGRESS_FILE.exists():
            self.save({})

    def load(self):
        """
        Charge la progression.
        """

        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return json.load(f)

    def save(self, data):
        """
        Sauvegarde la progression.
        """

        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

    def update(self, city, status):
        """
        Met à jour le statut d'une ville.
        """

        progress = self.load()

        progress[city] = status

        self.save(progress)

        logger.info(f"{city} -> {status}")

    def get_status(self, city):
        """
        Retourne le statut d'une ville.
        """

        progress = self.load()

        return progress.get(city, "pending")

    def is_completed(self, city):
        """
        Vérifie si une ville est déjà terminée.
        """

        return self.get_status(city) == "completed"

    def completed_cities(self):
        """
        Retourne toutes les villes terminées.
        """

        progress = self.load()

        return [
            city
            for city, status in progress.items()
            if status == "completed"
        ]

    def reset(self):
        """
        Réinitialise la progression.
        """

        self.save({})

        logger.info("Progression réinitialisée.")