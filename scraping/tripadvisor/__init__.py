"""
Package TripAdvisor.

Modules du scraper TripAdvisor.
"""

from .browser import Browser
from .search import Search
from .parser import Parser as TripAdvisorParser  # Alias pour compatibilité
from .mapper import Mapper
from .validator import Validator
from .storage import Storage
from .pipeline import Pipeline
from .scraper import TripAdvisorScraper

__all__ = [
    "Browser",
    "Search",
    "TripAdvisorParser",
    "Mapper",
    "Validator",
    "Storage",
    "Pipeline",
    "TripAdvisorScraper",
]