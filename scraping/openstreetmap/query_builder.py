"""
Construction des requêtes Overpass QL.

Responsabilités :
- Générer des requêtes Overpass QL valides
- Valider les paramètres
- Supporter plusieurs formats de recherche
"""

from typing import List
from scraping.common.logger import get_logger

logger = get_logger(__name__)


class OverpassQueryBuilder:
    """
    Générateur de requêtes Overpass QL valides.
    """

    DEFAULT_TAGS = [
        ("amenity", "restaurant"),
        ("amenity", "fast_food"),
        ("amenity", "cafe"),
        ("amenity", "food_court"),
        ("amenity", "bar"),
        ("amenity", "pub"),
    ]

    @staticmethod
    def area_query(country: str, city: str) -> str:
        """
        Recherche une ville comme zone administrative.

        Parameters
        ----------
        country : str
            Nom du pays
        city : str
            Nom de la ville

        Returns
        -------
        str
            Requête Overpass QL valide
        """
        query = f"""
[out:json][timeout:120];

area
["name"="{country}"]
->.country;

area
["name"="{city}"]
(area.country)
->.city;

out ids;
"""
        logger.debug(f"Requête area générée (len={len(query)})")
        return query

    @staticmethod
    def restaurants_query(
        area_id: int,
        tags: List[tuple] = None
    ) -> str:
        """
        Recherche tous les restaurants dans une zone administrative.
        
        Parameters
        ----------
        area_id : int
            ID de la zone (relation OSM + 3600000000)
        tags : List[tuple], optional
            Liste de (clé, valeur) OSM à chercher
            
        Returns
        -------
        str
            Requête Overpass QL valide
        """

        if tags is None:
            tags = OverpassQueryBuilder.DEFAULT_TAGS

        # Construction de la requête
        query = f"""
[out:json][timeout:180];

area({area_id})->.searchArea;

(
"""

        for key, value in tags:
            query += f"""
    node["{key}"="{value}"](area.searchArea);
    way["{key}"="{value}"](area.searchArea);
    relation["{key}"="{value}"](area.searchArea);
"""

        query += """
);

out center tags;
"""
        logger.debug(f"Requête restaurants générée (len={len(query)}, area_id={area_id})")
        return query

    @staticmethod
    def bbox_query(
        south: float,
        west: float,
        north: float,
        east: float,
        tags=None,
    ) -> str:
        """
        Recherche à partir d'une Bounding Box.
        """

        if tags is None:
            tags = OverpassQueryBuilder.DEFAULT_TAGS

        query = """
[out:json][timeout:180];

(
"""

        for key, value in tags:

            query += f"""
node["{key}"="{value}"]({south},{west},{north},{east});
way["{key}"="{value}"]({south},{west},{north},{east});
relation["{key}"="{value}"]({south},{west},{north},{east});
"""

        query += """
);

out center tags;
"""

        return query

    @staticmethod
    def custom_query(query: str):
        """
        Retourne une requête personnalisée.
        """
        return query