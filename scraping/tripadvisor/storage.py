"""
storage.py

Gestion du stockage des restaurants TripAdvisor.

Responsabilités
----------------
- Accumuler les restaurants extraits
- Supprimer les doublons
- Sauvegarder un seul CSV par pays
"""

from pathlib import Path

import pandas as pd # type:ignore

from scraping.common.logger import get_logger

logger = get_logger(__name__)


class Storage:

    def __init__(self, country: str):
        """
        Initialise le stockage.

        Parameters
        ----------
        country : str
            Nom du pays (morocco, qatar, ...)
        """

        self.country = country.lower()

        self.restaurants = []

        self.output_dir = Path("data/tripadvisor")
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # ---------------------------------------------------------

    def add(self, restaurants):
        """
        Ajoute les restaurants d'une ville.
        """

        if not restaurants:
            return

        self.restaurants.extend(restaurants)

        logger.info(
            "%s restaurants ajoutés (%s au total).",
            len(restaurants),
            len(self.restaurants)
        )

    # ---------------------------------------------------------

    def save(self):
        """
        Sauvegarde toutes les données dans un unique CSV.
        """

        if not self.restaurants:

            logger.warning(
                "Aucun restaurant à sauvegarder."
            )

            return

        df = pd.DataFrame(self.restaurants)

        # Suppression des doublons
        duplicate_columns = [
            col
            for col in (
                "tripadvisor_url",
                "name",
                "city"
            )
            if col in df.columns
        ]

        if duplicate_columns:

            before = len(df)

            df = df.drop_duplicates(
                subset=duplicate_columns
            )

            logger.info(
                "%s doublons supprimés.",
                before - len(df)
            )

        output_file = self.output_dir / f"{self.country}.csv"

        df.to_csv(
            output_file,
            index=False,
            encoding="utf-8-sig"
        )

        logger.info(
            "CSV sauvegardé : %s",
            output_file
        )

        logger.info(
            "%s restaurants enregistrés.",
            len(df)
        )

    # ---------------------------------------------------------

    def clear(self):
        """
        Vide la mémoire.
        """

        self.restaurants.clear()

        logger.info(
            "Stockage vidé."
        )

    # ---------------------------------------------------------

    def load(self) -> list[dict]:
        """
        Charge les restaurants depuis le fichier CSV du pays.
        """
        output_file = self.output_dir / f"{self.country}.csv"
        
        if not output_file.exists():
            logger.warning("Aucun fichier CSV trouvé pour : %s", output_file)
            return []

        df = pd.read_csv(output_file, encoding="utf-8-sig")
        
        # Remplace les NaN par None pour manipuler facilement les dictionnaires
        df = df.where(pd.notnull(df), None)
        
        self.restaurants = df.to_dict(orient="records")
        logger.info("%s restaurants chargés depuis %s", len(self.restaurants), output_file)
        
        return self.restaurants