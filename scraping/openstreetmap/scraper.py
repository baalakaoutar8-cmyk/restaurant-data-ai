"""
scraper.py

Orchestrateur du scraping OpenStreetMap.
"""

from pathlib import Path

import pandas as pd

from scraping.common.logger import get_logger
from scraping.common.progress import ProgressManager
from scraping.common.city_manager import CityManager
from scraping.common.utils import (
    save_csv,
    generate_filename,
)

from scraping.openstreetmap.nominatim import NominatimClient
from scraping.openstreetmap.overpass import OverpassClient
from scraping.openstreetmap.query_builder import OverpassQueryBuilder
from scraping.openstreetmap.parser import OSMParser


logger = get_logger(__name__)


class OpenStreetMapScraper:
    """
    Scraper OpenStreetMap.

    Fonctionne pour n'importe quel pays supporté simplement en
    changeant le paramètre `country` :

        scraper = OpenStreetMapScraper(country="uae")
        scraper = OpenStreetMapScraper(country="uae")

    Workflow :

        Ville
           ↓
      Nominatim
           ↓
        Area ID
           ↓
       Overpass
           ↓
         Parser
           ↓
           CSV
    """

    def __init__(
        self,
        country: str = "uae",
        priority: int | None = None,
        output_folder: Path | None = None,
    ):
        """
        Parameters
        ----------
        country : str
            Pays à scraper (ex : "morocco", "qatar", "saudi_arabia",
            "uae", "kuwait", "bahrain").

        priority : int | None
            Priorité des villes (1, 2, 3 ou None). Uniquement
            pertinent pour les pays disposant de priorités
            (le Maroc).

        output_folder : Path | None
            Dossier de sortie personnalisé.
        """

        self.country = country
        self.country_key = country.strip().lower().replace(" ", "_")
        self.priority = priority

        # Dossier de sortie

        if output_folder is None:
            self.output_folder = (
                Path("data/raw/openstreetmap")
                / self.country_key
            )
        else:
            self.output_folder = Path(output_folder)

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Clients

        self.nominatim = NominatimClient()
        self.overpass = OverpassClient()

        # Outils

        self.builder = OverpassQueryBuilder()
        self.parser = OSMParser()
        self.progress = ProgressManager()

        # Le CityManager reçoit désormais le pays, afin de charger
        # automatiquement le bon fichier JSON (priorités pour le
        # Maroc, fichier pays pour les autres).
        self.city_manager = CityManager(country=self.country)

        # Résultats

        self.restaurants = []
        self.total_restaurants = 0

        logger.info("=" * 80)
        logger.info("OpenStreetMap Scraper")
        logger.info(f"Country  : {self.country}")
        logger.info(f"Priority : {self.priority}")
        logger.info(f"Output   : {self.output_folder}")
        logger.info("=" * 80)

    # ==========================================================
    # Chargement des villes
    # ==========================================================

    def load_cities(self):
        """
        Retourne les villes à scraper.

        Le fichier JSON chargé par CityManager correspond déjà au
        pays courant (voir CityManager._resolve_filepath), donc
        aucun filtrage supplémentaire par pays n'est nécessaire ici.

        - priority is None -> toutes les villes du fichier.
        - priority défini -> uniquement les villes ayant cette
          priorité (pertinent pour le Maroc ; pour les autres pays,
          get_by_priority() renverra une liste vide si le champ
          "priority" est absent).
        """

        if self.priority is None:
            cities = self.city_manager.get_all()
        else:
            cities = self.city_manager.get_by_priority(
                self.priority
            )

        logger.info(
            f"{len(cities)} villes à traiter."
        )

        return cities

    # ==========================================================
    # Vérification progression
    # ==========================================================

    def should_skip(self, city_name: str):
        """
        Vérifie si une ville est déjà traitée.
        """

        return self.progress.is_completed(city_name)

    # ==========================================================
    # Sauvegarde intermédiaire
    # ==========================================================

    def save_intermediate(self):
        """
        Sauvegarde intermédiaire des restaurants récupérés.

        Un fichier est créé après chaque ville afin
        d'éviter toute perte de données en cas d'arrêt
        du scraping.
        """

        if not self.restaurants:
            return

        df = pd.DataFrame(self.restaurants)

        filename = (
            "intermediate/"
            + generate_filename(f"osm_restaurants_{self.country_key}")
        )

        save_csv(
            df=df,
            filename=filename,
        )

        logger.info(
            f"Sauvegarde intermédiaire : {len(df)} restaurants."
        )

    # ==========================================================
    # Fermeture
    # ==========================================================

    def close(self):
        """
        Ferme toutes les connexions.
        """

        try:
            self.nominatim.close()
        except Exception:
            pass

        try:
            self.overpass.close()
        except Exception:
            pass

        logger.info(
            "Toutes les connexions ont été fermées."
        )

    # ==========================================================
    # Scraping d'une ville
    # ==========================================================
    def scrape_city(self, city: dict):
        """Scrape une seule ville.

        Parameters
        ----------
        city : dict
            Informations de la ville.
        """

        city_name = city["city"]

        logger.info("=" * 70)
        logger.info(f"Début du scraping : {city_name}")
        logger.info("=" * 70)

        # --------------------------------------------------
        # Ville déjà traitée
        # --------------------------------------------------

        if self.should_skip(city_name):

            logger.info(
                f"{city_name} déjà traitée. Passage à la suivante."
            )

            return []

        self.progress.update(city_name, "running")

        try:

            # --------------------------------------------------
            # Recherche de la ville via Nominatim
            # --------------------------------------------------

            city_info = self.nominatim.get_city_information(
                city=city_name,
                country=self.country,
            )

            if city_info is None:

                logger.warning(
                    f"Ville introuvable : {city_name}"
                )

                self.progress.update(
                    city_name,
                    "failed",
                )

                return []

            area_id = city_info.get("area_id")

            # --------------------------------------------------
            # Construction de la requête Overpass
            #
            # Nominatim renvoie parfois un osm_type="node" au lieu
            # de "relation", ce qui ne permet pas de calculer
            # d'area_id. Dans ce cas, on bascule automatiquement
            # sur une requête par Bounding Box plutôt que
            # d'abandonner la ville.
            # --------------------------------------------------

            if area_id is not None:

                logger.info(f"Area ID : {area_id}")

                query = self.builder.restaurants_query(
                    area_id=area_id
                )

            else:

                bbox = city_info.get("bbox")

                if not bbox:

                    logger.warning(
                        f"Aucun Area ID ni Bounding Box "
                        f"trouvé pour {city_name}"
                    )

                    self.progress.update(
                        city_name,
                        "failed",
                    )

                    return []

                south, west, north, east = bbox

                logger.info(
                    f"Area ID indisponible, utilisation de la "
                    f"Bounding Box : south={south}, west={west}, "
                    f"north={north}, east={east}"
                )

                query = self.builder.bbox_query(
                    south,
                    west,
                    north,
                    east,
                )

            # --------------------------------------------------
            # Exécution de la requête
            # --------------------------------------------------

            elements = self.overpass.get_elements(query)

            logger.info(
                f"{len(elements)} éléments récupérés."
            )

            if not elements:

                logger.warning(
                    f"Aucun restaurant trouvé pour {city_name}"
                )

                self.progress.update(
                    city_name,
                    "completed",
                )

                return []

            # --------------------------------------------------
            # Parsing
            # --------------------------------------------------

            restaurants = self.parser.parse(
                elements=elements,
                country=self.country,
                city=city_name,
            )

            logger.info(
                f"{len(restaurants)} restaurants parsés."
            )

            # --------------------------------------------------
            # Stockage mémoire
            # --------------------------------------------------

            self.restaurants.extend(restaurants)

            self.total_restaurants += len(restaurants)

            # --------------------------------------------------
            # Progression
            # --------------------------------------------------

            self.progress.update(
                city_name,
                "completed",
            )

            logger.info(
                f"{city_name} terminé avec succès."
            )

            return restaurants

        except KeyboardInterrupt:

            logger.warning(
                "Scraping interrompu par l'utilisateur."
            )

            self.progress.update(
                city_name,
                "failed",
            )

            raise

        except Exception as e:

            logger.exception(
                f"Erreur pendant le scraping de {city_name} : {e}"
            )

            self.progress.update(
                city_name,
                "failed",
            )

            return []

    # ==========================================================
    # Scraping de plusieurs villes
    # ==========================================================

    def scrape_cities(self, cities):
        """
        Scrape une liste de villes.
        """

        all_restaurants = []

        total = len(cities)

        for index, city in enumerate(cities, start=1):

            logger.info(f"[{index}/{total}] {city['city']}")

            restaurants = self.scrape_city(city)

            all_restaurants.extend(restaurants)

            logger.info(
                f"Total actuel : {len(all_restaurants)} restaurants"
            )

            # Désactivé :
            # self.save_intermediate()

        return all_restaurants

    # ==========================================================
    # Export final
    # ==========================================================

    def export_results(self):
        """
        Sauvegarde le résultat final.

        Le fichier est enregistré dans :

        data/raw/openstreetmap/<country>/restaurants_<country>.csv
        """

        if not self.restaurants:

            logger.warning(
                "Aucun restaurant à sauvegarder."
            )

            return

        df = pd.DataFrame(self.restaurants)

        # Dossier créé dans __init__

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        filepath = (
            self.output_folder / f"restaurants_{self.country_key}.csv"
        )

        df.to_csv(
            filepath,
            index=False,
            encoding="utf-8-sig",
        )

        logger.info("=" * 80)
        logger.info("EXPORT TERMINÉ")
        logger.info("=" * 80)
        logger.info(
            f"{len(df)} restaurants sauvegardés."
        )
        logger.info(
            f"Fichier : {filepath.resolve()}"
        )

    # ==========================================================
    # Résumé
    # ==========================================================

    def summary(self):
        """
        Affiche le résumé du scraping.
        """

        logger.info("=" * 80)
        logger.info("SCRAPING TERMINÉ")
        logger.info("=" * 80)

        logger.info(
            f"Pays : {self.country}"
        )

        logger.info(
            f"Restaurants récupérés : {self.total_restaurants}"
        )

        logger.info(
            f"Restaurants en mémoire : {len(self.restaurants)}"
        )

        logger.info(
            f"Dossier de sortie : {self.output_folder}"
        )

        logger.info("=" * 80)

    # ==========================================================
    # Lancement principal
    # ==========================================================

    def run(self):
        """
        Lance le scraping complet.
        """

        logger.info("=" * 80)
        logger.info("DÉMARRAGE DU SCRAPING")
        logger.info("=" * 80)

        try:

            logger.info("Chargement des villes...")

            cities = self.load_cities()

            if not cities:

                logger.warning(
                    "Aucune ville trouvée."
                )

                return []

            logger.info(
                f"{len(cities)} villes à traiter."
            )

            self.scrape_cities(cities)

            self.export_results()

            self.summary()

            return self.restaurants

        except KeyboardInterrupt:

            logger.warning(
                "Scraping interrompu par l'utilisateur."
            )

            return self.restaurants

        except Exception:

            logger.exception(
                "Erreur inattendue durant le scraping."
            )

            raise

        finally:

            self.close()

    # ==========================================================
    # Réinitialisation de la progression
    # ==========================================================

    def reset_progress(self):
        """
        Réinitialise la progression.
        """

        self.progress.reset()

        logger.info(
            "Progression réinitialisée."
        )


# ==========================================================
# Exécution directe
# ==========================================================

if __name__ == "__main__":

    scraper = OpenStreetMapScraper(

        country="uae",

        priority=None,

    )

    scraper.run()