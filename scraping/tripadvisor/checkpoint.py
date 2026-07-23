"""
checkpoint.py

Gestion de la reprise du scraping.

Responsabilités
----------------
- Sauvegarder la progression
- Reprendre après un arrêt
"""

import json
from pathlib import Path

from scraping.common.logger import get_logger

logger = get_logger(__name__)


class Checkpoint:
    FILE = Path("data/checkpoint.json")

    @classmethod
    def save(cls, country: str, city_index: int):
        """
        Sauvegarde la progression.
        """

        cls.FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = {
            "country": country,
            "city_index": city_index
        }

        with open(
            cls.FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

        logger.info(
            "Checkpoint sauvegardé (%s - ville %s).",
            country,
            city_index
        )

    @classmethod
    def load(cls):
        """
        Charge le dernier checkpoint.
        """

        if not cls.FILE.exists():

            logger.info(
                "Aucun checkpoint trouvé."
            )

            return None

        with open(
            cls.FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        logger.info(
            "Checkpoint chargé : %s",
            data
        )

        return data

    @classmethod
    def clear(cls):
        """
        Supprime le checkpoint.
        """

        if cls.FILE.exists():

            cls.FILE.unlink()

            logger.info(
                "Checkpoint supprimé."
            )