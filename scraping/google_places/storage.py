"""
storage.py

Gestion du stockage des restaurants TripAdvisor.

Responsabilités
----------------
- Accumuler les restaurants provenant de toutes les villes d'un pays.
- Éviter les doublons (optionnel).
- Sauvegarder un unique fichier CSV : <country>.csv
"""

from pathlib import Path
import pandas as pd

from scraping.common.logger import get_logger

logger = get_logger(__name__)


class Storage:
    """
    Stocke les restaurants d'un pays en mémoire,
    puis les écrit dans un seul fichier CSV.
    """

    def __init__(self):

        self.restaurants = []

    def add(self, restaurants):
        """
        Ajoute les restaurants d'une ville.

        Parameters
        ----------
        restaurants : list[dict]
        """

        if not restaurants:
            return

        self.restaurants.extend(restaurants)

    def save(self, country):
        """
        Sauvegarde tous les restaurants dans un fichier CSV.

        Parameters
        ----------
        country : str
            Exemple : "morocco"
        """

        if not self.restaurants:
            logger.warning("Aucun restaurant à sauvegarder.")
            return

        df = pd.DataFrame(self.restaurants)

        # Suppression des doublons (par nom + ville + adresse)
        duplicate_columns = [
            col
            for col in ["name", "city", "address"]
            if col in df.columns
        ]

        if duplicate_columns:
            df = df.drop_duplicates(subset=duplicate_columns)

        output_dir = Path("data/tripadvisor")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{country.lower()}.csv"

        df.to_csv(output_file, index=False, encoding="utf-8-sig")

        logger.info(
            "%s restaurants sauvegardés dans %s",
            len(df),
            output_file
        )

    def clear(self):
        """
        Vide la mémoire.
        """

        self.restaurants.clear()