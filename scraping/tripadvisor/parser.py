"""
scraping/tripadvisor/parser.py

Parser BeautifulSoup / Playwright pour extraire les fiches restaurants TripAdvisor.
"""

import logging
import re
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup  # type: ignore

logger = logging.getLogger(__name__)


class TripAdvisorParser:
    """Parser pour extraire les informations des cartes de restaurants TripAdvisor."""

    def __init__(
        self,
        page_or_html: Any,
        city_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.city_name: Optional[str] = city_name

        if hasattr(page_or_html, "content"):
            html_content = page_or_html.content()
            self._page = page_or_html
        elif isinstance(page_or_html, str):
            html_content = page_or_html
            self._page = None
        else:
            html_content = ""
            self._page = None

        self.soup = BeautifulSoup(html_content, "html.parser")

    def parse_restaurant_card(self, card: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extrait les données d'un conteneur ou d'une balise lien de restaurant."""
        try:
            if card.name == "a":
                link_elem = card
            else:
                link_elem = card.select_one("a[href*='/Restaurant_Review']")

            if not link_elem:
                return None

            url = link_elem.get("href", "")
            if not url:
                return None

            if not url.startswith("http"):
                url = f"https://www.tripadvisor.com{url}"

            name = link_elem.get_text(strip=True)

            # 🛑 Filtre anti-bruit : Si le nom pointe vers un lien d'avis ou est vide/numérique
            if not name or re.search(r"reviews?|avis", name, re.IGNORECASE) or name.startswith("("):
                # On tente de trouver un vrai titre dans le conteneur parent
                heading = card.select_one('h3, h4, div[class*="title"]')
                if heading:
                    name = heading.get_text(strip=True)
                else:
                    # Si c'est un simple lien <a> pointant vers un compteur de reviews, on l'ignore
                    return None

            # Re-vérification stricte du nom nettoyé
            if not name or re.search(r"reviews?|avis", name, re.IGNORECASE) or name.startswith("("):
                return None

            # Nettoyage du préfixe numéroté (ex: "1. Le Restaurant" -> "Le Restaurant")
            name = re.sub(r"^\d+\.\s*", "", name)

            # Extraction de la note
            rating = None
            rating_elem = card.select_one("svg[title*='bubbles'], span[class*='bubble']")
            if rating_elem:
                rating_text = rating_elem.get("title", "") or rating_elem.get_text()
                match = re.search(r"(\d+([.,]\d+)?)", rating_text)
                if match:
                    rating = float(match.group(1).replace(",", "."))

            # Extraction du nombre d'avis
            reviews_count = None
            reviews_elem = card.select_one("span[class*='review'], a[href*='Reviews']")
            if reviews_elem:
                rev_text = reviews_elem.get_text(strip=True)
                rev_match = re.search(r"([\d\s\u00a0,.]+)", rev_text)
                if rev_match:
                    clean_num = re.sub(r"[^\d]", "", rev_match.group(1))
                    if clean_num:
                        reviews_count = int(clean_num)

            # Prix et type de cuisine
            price_level = None
            cuisines = []
            info_elems = card.select("span[class*='price'], div[class*='cuisine']")

            for elem in info_elems:
                text = elem.get_text(strip=True)
                if "$" in text or "€" in text or "KWD" in text:
                    price_level = text
                elif text:
                    cuisines.append(text)

            return {
                "name": name,
                "url": url,
                "tripadvisor_url": url,
                "rating": rating,
                "reviews_count": reviews_count,
                "price_level": price_level,
                "cuisines": cuisines,
                "city": self.city_name,
            }

        except Exception as e:
            logger.error(f"Erreur lors du parsing d'une carte: {e}")
            return None

    def parse_all(self) -> List[Dict[str, Any]]:
        """Extrait tous les restaurants de la page en ciblant les conteneurs ou liens."""
        if self._page:
            self.soup = BeautifulSoup(self._page.content(), "html.parser")

        results = []

        # 1. Tentative sur les conteneurs de cartes
        cards = self.soup.select(
            "div[data-automation='hotel-card'], "
            "div[data-automation='listing_card'], "
            "div[data-test-target='restaurants-list-item'], "
            "div[class*='list_item'], "
            "div[class*='listItem']"
        )

        # 2. Fallback sur les balises <a> directes
        if not cards:
            cards = self.soup.select('a[href*="/Restaurant_Review-"]')

        for card in cards:
            parsed_data = self.parse_restaurant_card(card)
            if parsed_data and parsed_data.get("name") and parsed_data.get("url"):
                results.append(parsed_data)

        return results

    def parse_page_deduplicated(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """Extrait tous les restaurants de la page en éliminant les doublons."""
        all_restaurants = self.parse_all()
        seen = set()
        unique_restaurants = []

        for item in all_restaurants:
            # Normalisation de l'URL pour le dédoublonnage (ignore les paramètres de requête)
            raw_url = item.get("url", "")
            clean_url = raw_url.split("?")[0].split("#")[0] if raw_url else item.get("name")

            if clean_url and clean_url not in seen:
                seen.add(clean_url)
                unique_restaurants.append(item)

        logger.info(f"Parsé {len(unique_restaurants)} restaurants uniques sur la page.")
        return unique_restaurants

    def parse_detail(self, city_name: Optional[str] = None) -> Dict[str, Any]:
        """Extrait les informations détaillées d'une page de restaurant."""
        if self._page:
            self.soup = BeautifulSoup(self._page.content(), "html.parser")

        details: Dict[str, Any] = {
            "city": city_name or self.city_name,
            "address": None,
            "phone": None,
            "website": None,
            "hours": [],
        }

        addr_elem = self.soup.select_one("a[href*='#MAP'], span[class*='address']")
        if addr_elem:
            details["address"] = addr_elem.get_text(strip=True)

        phone_elem = self.soup.select_one("a[href^='tel:']")
        if phone_elem:
            details["phone"] = phone_elem.get_text(strip=True)

        return details

    def parse_listing(self, city_name: Optional[str] = None, country_name: str = "UAE") -> List[Dict[str, Any]]:
        if city_name:
            self.city_name = city_name
        return self.parse_page_deduplicated()

    def parse(self, city_name: Optional[str] = None, country_name: str = "UAE") -> List[Dict[str, Any]]:
        return self.parse_page_deduplicated()


# Alias pour rétrocompatibilité
Parser = TripAdvisorParser