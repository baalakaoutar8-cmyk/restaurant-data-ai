"""
loader.py

Charge la liste des villes pour un pays donné à partir de config/cities.py.
"""

import config.cities as cities_config
from scraping.common.logger import get_logger

logger = get_logger(__name__)


class CountryLoader:

    @staticmethod
    def load_cities(country_code: str) -> list[str]:
        """
        Récupère la liste des villes pour un pays depuis config/cities.py.
        Exemple : 'qatar' -> cherche QATAR_CITIES ou l'entrée 'qatar' dans CITIES_BY_COUNTRY.
        """
        country_key = country_code.lower()

        # 1. Vérification dans le dictionnaire CITIES_BY_COUNTRY s'il existe
        if hasattr(cities_config, "CITIES_BY_COUNTRY"):
            if country_key in cities_config.CITIES_BY_COUNTRY:
                return cities_config.CITIES_BY_COUNTRY[country_key]

        # 2. Recherche d'une variable au format <PAYS>_CITIES (ex: QATAR_CITIES)
        var_name = f"{country_code.upper()}_CITIES"
        if hasattr(cities_config, var_name):
            return getattr(cities_config, var_name)

        logger.error(f"Aucune liste de villes trouvée dans config/cities.py pour '{country_code}'")
        raise AttributeError(
            f"Veuillez définir '{var_name}' ou l'ajouter dans 'CITIES_BY_COUNTRY' dans config/cities.py."
        )