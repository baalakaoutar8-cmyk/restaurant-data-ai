"""
Search module for TripAdvisor scraping.
Bypasses buggy search forms by leveraging direct GEO-ID mappings or canonical URLs.
"""

from __future__ import annotations

import urllib.parse
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError  # type:ignore

from scraping.common.human import short_pause, medium_pause
from scraping.common.logger import get_logger

logger = get_logger(__name__)

_BASE_URL: str = "https://www.tripadvisor.com"

# Mapping direct des villes fréquemment scrapées vers leur URL canonique TripAdvisor
_KNOWN_CITY_URLS: dict[str, str] = {
    "kuwait city": "https://www.tripadvisor.com/Restaurants-g294003-Kuwait_City.html",
    "doha": "https://www.tripadvisor.com/Restaurants-g294009-Doha.html",
    "casablanca": "https://www.tripadvisor.com/Restaurants-g293732-Casablanca_Grand_Casablanca_Region.html",
    "dubai": "https://www.tripadvisor.com/Restaurants-g295424-Dubai_Emirate_of_Dubai.html",
    "abu dhabi": "https://www.tripadvisor.com/Restaurants-g295423-Abu_Dhabi_Emirate_of_Abu_Dhabi.html",
    "riyadh": "https://www.tripadvisor.com/Restaurants-g293995-Riyadh_Riyadh_Province.html",
}

_COOKIE_ACCEPT_BUTTONS: tuple[str, ...] = (
    'button:has-text("Accept")',
    'button:has-text("Accept All")',
    'button:has-text("I accept")',
    'button:has-text("Agree")',
    'button:has-text("Tout accepter")',
    'button:has-text("Accepter")',
    '[id*="onetrust-accept"]',
)


class Search:
    """Search for a city on TripAdvisor and navigate to its restaurant section."""

    def __init__(self, page: Page) -> None:
        if page is None:
            raise ValueError("Page instance must not be None.")
        self._page: Page = page

    def search(self, city: str) -> bool:
        """Execute location search and land directly on the Restaurants page."""
        logger.info("Starting location search for city: %s", city)
        city_clean = city.strip().lower()

        try:
            # Estratégie 1 : Utilisation de l'URL directe connue (Méthode instantanée)
            if city_clean in _KNOWN_CITY_URLS:
                target_url = _KNOWN_CITY_URLS[city_clean]
                logger.info("Using direct canonical URL for %s: %s", city, target_url)
                self._page.goto(target_url, wait_until="domcontentloaded", timeout=30_000)
                short_pause()
                self._dismiss_cookie_banner_if_present()

            # Estratégie 2 : Fallback de recherche générique si la ville n'est pas dans le dictionnaire
            else:
                encoded_city = urllib.parse.quote(f"{city} restaurants")
                search_url = f"{_BASE_URL}/Search?q={encoded_city}"
                logger.info("City not in known list. Navigating to search URL: %s", search_url)

                self._page.goto(search_url, wait_until="domcontentloaded", timeout=30_000)
                short_pause()
                self._dismiss_cookie_banner_if_present()

                if not self._click_first_search_result(city):
                    logger.warning("Could not locate restaurant results for %s", city)
                    return False

            # Validation finale qu'on est bien sur la page des restaurants
            if not self._validate_restaurant_listings_present():
                logger.warning("Listing validation failed for %s. Current URL: %s", city, self._page.url)
                return False

        except PlaywrightTimeoutError as exc:
            logger.warning("Timeout error during navigation for '%s': %s", city, exc)
            return False
        except Exception as exc:
            logger.error("Unexpected error during search for '%s': %s", city, exc, exc_info=True)
            return False

        logger.info("Successfully landed on restaurant listings for: %s (URL: %s)", city, self._page.url)
        return True

    def _dismiss_cookie_banner_if_present(self) -> None:
        for selector in _COOKIE_ACCEPT_BUTTONS:
            try:
                locator = self._page.locator(selector).first
                if locator.is_visible(timeout=1_500):
                    logger.info("Dismissing cookie banner: %s", selector)
                    locator.click(force=True)
                    short_pause()
                    return
            except Exception:
                continue

    def _click_first_search_result(self, city: str) -> bool:
        """Fallback pour interagir avec les éléments si la recherche globale est utilisée."""
        try:
            link = self._page.locator('a[href*="/Restaurants-g"], a[href*="/Restaurant_Review-g"]').first
            if link.is_visible(timeout=5_000):
                link.click(force=True)
                medium_pause()
                return True
        except Exception:
            pass
        return False

    def _validate_restaurant_listings_present(self) -> bool:
        """Vérifie si la page actuelle contient bien des cartes ou des liens de restaurants."""
        self._page.wait_for_load_state("domcontentloaded", timeout=15_000)

        if "/Restaurants-g" in self._page.url:
            logger.info("URL validation passed: %s", self._page.url)

        card_selectors = (
            'a[href*="Restaurant_Review"]',
            '[data-test-target="restaurants-list"]',
            '[data-automation="restaurant_card"]',
            'div[data-data-type="Restaurant"]',
            'div[class*="list"] a[href*="Restaurant_Review"]',
            'a[href*="-d"]',
        )

        for selector in card_selectors:
            try:
                locator = self._page.locator(selector).first
                if locator.is_visible(timeout=5_000):
                    logger.info("Listing cards verified on page via: %s", selector)
                    return True
            except Exception:
                continue

        # Fallback de secours si l'URL est correcte
        if "/Restaurants-g" in self._page.url:
            logger.warning("Selectors missed, but validated based on URL marker '/Restaurants-g'")
            return True

        return False