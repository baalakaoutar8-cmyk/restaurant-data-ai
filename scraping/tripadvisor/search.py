"""
Search module for TripAdvisor scraping.

Handles navigation to TripAdvisor, location search, landing on the location's
hub, and navigating into the dedicated Restaurants category page.
"""

from __future__ import annotations

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError  # type:ignore

from scraping.common.human import short_pause, medium_pause, long_pause
from scraping.common.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Selectors (TripAdvisor Modern UX Layout)
# ---------------------------------------------------------------------------

# Trigger button if search input isn't rendered in DOM immediately
_SEARCH_TRIGGER_BUTTONS: tuple[str, ...] = (
    'button[aria-label*="Search"]',
    'button[aria-label*="Rechercher"]',
    'a[aria-label*="Search"]',
    '[data-aria-label*="Search"]',
    'form[role="search"]',
)

# Search input elements
_SEARCH_INPUT_SELECTORS: tuple[str, ...] = (
    'input[type="search"]',
    'input[placeholder*="Where to"]',
    'input[placeholder*="Où allez-vous"]',
    'input[placeholder*="Places to go"]',
    'input[placeholder*="Search"]',
    'input[name="q"]',
)

# Suggestion overlays
_SUGGESTIONS_CONTAINER: str = (
    '[data-automation="typeahead_results"], '
    '[data-testid="typeahead"], '
    '[class*="typeahead"], '
    'ul[role="listbox"]'
)
_SUGGESTION_ITEM: str = (
    '[data-automation="suggestionItem"], '
    '[data-testid="suggestion"], '
    'li[role="option"], '
    'ul[role="listbox"] li'
)

# Tab triggers for Restaurants on the destination landing page
_RESTAURANT_TAB_SELECTORS: tuple[str, ...] = (
    'a:has-text("Restaurants")',
    'button:has-text("Restaurants")',
    'a[href*="Restaurants-g"]',
    '[data-tab-name="Restaurants"]',
    'span:has-text("Restaurants")',
)

# Final page verification marker
_RESTAURANTS_URL_MARKER: str = "/Restaurants-g"

# GDPR / Cookie selectors
_COOKIE_ACCEPT_BUTTONS: tuple[str, ...] = (
    'button:has-text("Accept")',
    'button:has-text("Accept All")',
    'button:has-text("I accept")',
    'button:has-text("Agree")',
    'button:has-text("Tout accepter")',
    'button:has-text("Accepter")',
    '[id*="onetrust-accept"]',
)

_BASE_URL: str = "https://www.tripadvisor.com"


class Search:
    """Search for a city on TripAdvisor and navigate to its restaurant section."""

    def __init__(self, page: Page) -> None:
        if page is None:
            raise ValueError("Page instance must not be None.")
        self._page: Page = page
        logger.debug("Search instance initialized with page URL: %s", page.url)

    def search(self, city: str) -> bool:
        """Execute location search, select the city, and open the Restaurants tab.

        Args:
            city: The target city (e.g. "Doha", "Casablanca", "Dibba Al Hisn").

        Returns:
            True if successfully landed on the city's /Restaurants-g page with
            listing content ready for Parser.
        """
        logger.info("Starting location search for city: %s", city)

        try:
            self._open_homepage()
            self._dismiss_cookie_banner_if_present()

            # 1. Focus search input (opening trigger modal/overlay if required)
            search_input = self._resolve_search_input()

            # 2. Type location name ONLY (e.g. "Dibba Al Hisn")
            self._type_query(search_input, city)

            # 3. Wait & select city suggestion
            if self._wait_for_suggestions(timeout_ms=6_000):
                self._select_location_suggestion(city)
            else:
                logger.warning("No suggestions appeared for '%s'. Submitting form directly.", city)
                search_input.press("Enter")
                medium_pause()

            # 4. Once on the city destination page, click on the "Restaurants" tab
            logger.info("Navigating to Restaurants tab for %s...", city)
            if not self._open_restaurants_tab():
                logger.warning("Could not locate or click Restaurants tab for '%s'.", city)
                return False

            # 5. Final check: verify we are on /Restaurants-g and cards are visible
            if not self._validate_restaurant_listings_present():
                logger.warning("Failed final validation for restaurant listings in '%s'.", city)
                return False

        except PlaywrightTimeoutError as exc:
            logger.warning("Timeout error during search workflow for '%s': %s", city, exc)
            return False
        except Exception as exc:
            logger.error("Unexpected error during search for '%s': %s", city, exc, exc_info=True)
            return False

        logger.info("Successfully landed on restaurant listings for: %s", city)
        return True

    # ------------------------------------------------------------------
    # Internal Steps
    # ------------------------------------------------------------------

    def _open_homepage(self) -> None:
        """Navigate to base URL with domcontentloaded wait state."""
        logger.info("Navigating to %s", _BASE_URL)
        self._page.goto(_BASE_URL, wait_until="domcontentloaded", timeout=30_000)
        short_pause()

    def _dismiss_cookie_banner_if_present(self) -> None:
        """Best-effort banner dismissal."""
        for selector in _COOKIE_ACCEPT_BUTTONS:
            try:
                locator = self._page.locator(selector).first
                if locator.is_visible(timeout=1_500):
                    logger.info("Dismissing cookie banner: %s", selector)
                    locator.click()
                    short_pause()
                    return
            except Exception:
                continue

    def _resolve_search_input(self):
        """Locates search input. Clicks trigger button first if input isn't visible yet."""
        # Check if input is already visible
        for selector in _SEARCH_INPUT_SELECTORS:
            try:
                locator = self._page.locator(selector).first
                if locator.is_visible(timeout=1_000):
                    logger.debug("Resolved search input directly: %s", selector)
                    return locator
            except Exception:
                continue

        # If not visible, click the search trigger/icon first
        logger.debug("Input not immediately visible. Attempting to click search trigger button...")
        for trigger_selector in _SEARCH_TRIGGER_BUTTONS:
            try:
                trigger = self._page.locator(trigger_selector).first
                if trigger.is_visible(timeout=1_500):
                    trigger.click()
                    short_pause()
                    break
            except Exception:
                continue

        # Re-try finding search input after clicking trigger
        for selector in _SEARCH_INPUT_SELECTORS:
            try:
                locator = self._page.locator(selector).first
                if locator.is_visible(timeout=2_000):
                    logger.debug("Resolved search input post-trigger click: %s", selector)
                    return locator
            except Exception:
                continue

        raise RuntimeError("Could not resolve search input element on TripAdvisor.")

    def _type_query(self, search_input, query: str) -> None:
        """Type location query character-by-character."""
        logger.info("Typing location query: '%s'", query)
        search_input.click()
        search_input.fill("")
        search_input.press_sequentially(query, delay=60)
        short_pause()

    def _wait_for_suggestions(self, timeout_ms: int = 6_000) -> bool:
        """Wait for typeahead suggestions to populate."""
        try:
            container = self._page.locator(_SUGGESTIONS_CONTAINER).first
            container.wait_for(state="visible", timeout=timeout_ms)
            return self._page.locator(_SUGGESTION_ITEM).count() > 0
        except PlaywrightTimeoutError:
            return False

    def _select_location_suggestion(self, city: str) -> None:
        """Select first suggestion matching city name or default to top result."""
        items = self._page.locator(_SUGGESTION_ITEM)
        count = items.count()

        if count == 0:
            return

        for idx in range(min(count, 5)):
            try:
                item = items.nth(idx)
                text = item.inner_text(timeout=2_000).lower()
                if city.lower() in text:
                    logger.info("Selecting location suggestion %d: '%s'", idx + 1, text.strip())
                    item.click()
                    medium_pause()
                    return
            except Exception:
                continue

        # Fallback to top option
        logger.warning("No explicit match for '%s' in typeahead. Clicking first suggestion.", city)
        items.first.click()
        medium_pause()

    def _open_restaurants_tab(self) -> bool:
        """Click on Restaurants section from destination/city page."""
        # Wait a moment for destination page render
        self._page.wait_for_load_state("domcontentloaded", timeout=15_000)

        # If already on /Restaurants-g page, return early
        if _RESTAURANTS_URL_MARKER in self._page.url:
            logger.info("Already on Restaurants destination page.")
            return True

        for selector in _RESTAURANT_TAB_SELECTORS:
            try:
                item = self._page.locator(selector).first
                if item.is_visible(timeout=3_000):
                    logger.info("Clicking Restaurants tab via selector: %s", selector)
                    item.click()
                    medium_pause()
                    return True
            except Exception:
                continue

        return False

    def _validate_restaurant_listings_present(self) -> bool:
        """Ensure current page is a /Restaurants-g URL and contains card DOM elements."""
        if _RESTAURANTS_URL_MARKER not in self._page.url:
            logger.warning("Current URL missing '%s' marker: %s", _RESTAURANTS_URL_MARKER, self._page.url)

        card_selectors = (
            'div:has(a[href*="Restaurant_Review"])',
            '[data-testid="card"]',
            '[data-automation="listing_card"]',
            '[class*="result"]',
            '.listing',
        )

        for selector in card_selectors:
            try:
                locator = self._page.locator(selector).first
                if locator.is_visible(timeout=5_000):
                    logger.debug("Listing cards verified on page via: %s", selector)
                    return True
            except Exception:
                continue

        return False