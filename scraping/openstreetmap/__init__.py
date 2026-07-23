"""
OpenStreetMap Scraper Package.

Ce package permet de collecter les restaurants via
OpenStreetMap (Overpass API + Nominatim).
"""

from .nominatim import NominatimClient
from .overpass import OverpassClient
from .parser import OSMParser
from .query_builder import OverpassQueryBuilder
from .scraper import OpenStreetMapScraper

__all__ = [
    "NominatimClient",
    "OverpassClient",
    "OSMParser",
    "OverpassQueryBuilder",
    "OpenStreetMapScraper",
]

__version__ = "1.0.0"

__author__ = "Kaoutar Baala"