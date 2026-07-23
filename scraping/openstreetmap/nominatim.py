"""
nominatim.py

Client pour l'API Nominatim d'OpenStreetMap.

Responsabilités :
- Rechercher une ville
- Récupérer ses coordonnées
- Récupérer sa Bounding Box
- Récupérer son OSM ID
"""

from typing import Dict, Optional

from scraping.common.request_manager import RequestManager
from scraping.common.retry import retry
from scraping.common.rate_limiter import rate_limiter
from scraping.common.logger import get_logger

logger = get_logger(__name__)


class NominatimClient:
    """
    Client de l'API Nominatim.
    """

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def __init__(self):
        self.request = RequestManager()

    # =====================================================

    @retry()
    def search(
        self,
        city: str,
        country: str,
        limit: int = 10,
    ) -> Optional[Dict]:
        """
        Recherche une ville dans Nominatim.

        Retourne en priorité une relation OSM.
        """

        rate_limiter.pause()

        params = {
            "q": f"{city}, {country}",
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": limit,
        }

        logger.info(
            f"Nominatim : recherche de {city}, {country}"
        )

        response = self.request.get(
            self.BASE_URL,
            params=params,
        )

        data = response.json()

        if not data:
            logger.warning(
                f"Aucun résultat pour {city}"
            )
            return None

        # priorité aux relations
        for item in data:

            if item.get("osm_type") == "relation":

                logger.info(
                    f"Nominatim : relation trouvée "
                    f"(osm_id={item['osm_id']})"
                )

                return item

        logger.warning(
            f"Aucune relation trouvée pour {city}. "
            "Utilisation du meilleur résultat."
        )

        return data[0]

    # =====================================================

    def get_coordinates(
        self,
        city: str,
        country: str,
    ):

        result = self.search(city, country)

        if result is None:
            return None

        return (
            float(result["lat"]),
            float(result["lon"]),
        )

    # =====================================================

    def get_bbox(
        self,
        city: str,
        country: str,
    ):

        result = self.search(city, country)

        if result is None:
            return None

        bbox = result["boundingbox"]

        return (
            float(bbox[0]),
            float(bbox[2]),
            float(bbox[1]),
            float(bbox[3]),
        )

    # =====================================================

    def get_osm_id(
        self,
        city: str,
        country: str,
    ):

        result = self.search(city, country)

        if result is None:
            return None

        return int(result["osm_id"])

    # =====================================================

    def get_area_id(
        self,
        city: str,
        country: str,
    ):

        result = self.search(city, country)

        if result is None:
            return None

        osm_type = result["osm_type"]

        if osm_type != "relation":

            logger.warning(
                f"Nominatim : {city} est un {osm_type}, "
                "pas une relation."
            )

            return None

        osm_id = int(result["osm_id"])

        area_id = 3600000000 + osm_id

        logger.debug(
            f"Nominatim : area_id={area_id}"
        )

        return area_id

    # =====================================================

    def get_city_information(
        self,
        city: str,
        country: str,
    ):

        result = self.search(city, country)

        if result is None:

            logger.warning(
                f"get_city_information : {city} introuvable"
            )

            return None

        bbox = result["boundingbox"]

        osm_id = int(result["osm_id"])
        osm_type = result["osm_type"]

        area_id = None

        if osm_type == "relation":

            area_id = 3600000000 + osm_id

        else:

            logger.warning(
                f"{city} est un {osm_type}. "
                "Le scraper utilisera la Bounding Box."
            )

        info = {
            "country": country,
            "city": city,
            "latitude": float(result["lat"]),
            "longitude": float(result["lon"]),
            "osm_id": osm_id,
            "osm_type": osm_type,
            "display_name": result["display_name"],
            "bbox": {
                "south": float(bbox[0]),
                "north": float(bbox[1]),
                "west": float(bbox[2]),
                "east": float(bbox[3]),
            },
            "area_id": area_id,
        }

        return info

    # =====================================================

    def close(self):

        self.request.close()