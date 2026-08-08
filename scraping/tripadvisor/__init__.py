"""
Parser module for TripAdvisor scraping.

Provides parsing capability for:
1. Listing pages (Extracting list of restaurant preview cards & URLs).
2. Detail pages (Extracting complete metadata, GPS, phone, opening hours,
   ratings distribution, and user reviews matching specs).
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

from bs4 import BeautifulSoup  # type: ignore
from playwright.sync_api import Page  # type: ignore

from scraping.common.logger import get_logger

logger = get_logger(__name__)


class TripAdvisorParser:
    """Parses TripAdvisor listing and detail pages."""

    def __init__(self, page: Page, city_name: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize Parser with Playwright Page instance."""
        if page is None:
            raise ValueError("Page instance must not be None.")
        self._page: Page = page
        self.city_name: Optional[str] = city_name

    # =========================================================================
    # 1. LISTING PAGE PARSING (Phase 1)
    # =========================================================================

    def parse_listing(self, city_name: Optional[str] = None, country_name: str = "UAE") -> List[Dict[str, Any]]:
        """Extract basic restaurant items from a listing/search result page."""
        target_city = city_name or self.city_name or ""
        html_content = self._page.content()
        soup = BeautifulSoup(html_content, "html.parser")
        restaurants: List[Dict[str, Any]] = []

        cards = soup.select(
            'div[data-automation="listing_card"], '
            'div[data-test-target="restaurants-list-item"], '
            'div[class*="listItem"]'
        )

        seen_urls = set()

        for card in cards:
            try:
                # 1. Recherche prioritaire du lien avec le nom (évite de prendre le lien des reviews)
                link_elem = (
                    card.select_one('a[href*="Restaurant_Review"][class*="title"]')
                    or card.select_one('div[class*="title"] a[href*="Restaurant_Review"]')
                    or card.select_one('a[href*="Restaurant_Review"]:not([href*="#REVIEWS"])')
                    or card.select_one('a[href*="Restaurant_Review"]')
                )

                if not link_elem or not link_elem.get("href"):
                    continue

                raw_href = link_elem["href"]
                full_url = raw_href if raw_href.startswith("http") else f"https://www.tripadvisor.com{raw_href}"
                clean_url = full_url.split("?")[0]

                if clean_url in seen_urls:
                    continue

                # Extraction propre du nom
                name = link_elem.get_text(strip=True)
                # Si le nom extrait est du type "(217 reviews)", chercher un autre élément H3/H4 dans la carte
                if not name or re.match(r"^\(\d+.*reviews?\)$", name, re.IGNORECASE):
                    heading = card.select_one('h3, h4, div[class*="title"]')
                    if heading:
                        name = heading.get_text(strip=True)

                # Invalidation si ce n'est toujours pas un vrai nom
                if not name or re.match(r"^\(\d+.*reviews?\)$", name, re.IGNORECASE):
                    continue

                # Nettoyage des numéros d'ordre (ex: "1. Nusr-Et" -> "Nusr-Et")
                name = re.sub(r"^\d+\.\s*", "", name)
                seen_urls.add(clean_url)

                restaurants.append({
                    "name": name,
                    "country": country_name,
                    "city": target_city,
                    "tripadvisor_url": clean_url,
                })
            except Exception as exc:
                logger.debug("Error parsing card in listing: %s", exc)
                continue

        logger.info("Parsed %d restaurant links from listing page for %s", len(restaurants), target_city)
        return restaurants

    def parse(self, city_name: Optional[str] = None, country_name: str = "UAE") -> List[Dict[str, Any]]:
        return self.parse_listing(city_name, country_name)

    def parse_page_deduplicated(self, city_name: Optional[str] = None, country_name: str = "UAE") -> List[Dict[str, Any]]:
        return self.parse_listing(city_name, country_name)

    # =========================================================================
    # 2. DETAIL PAGE PARSING (Phase 2)
    # =========================================================================

    def parse_detail(self, city_name: str = "", country_name: str = "UAE") -> Dict[str, Any]:
        """Parse complete restaurant details from a detail page."""
        html_content = self._page.content()
        soup = BeautifulSoup(html_content, "html.parser")

        json_ld_data = self._extract_json_ld(soup)
        target_city = city_name or self.city_name or ""

        data: Dict[str, Any] = {
            "name": self._extract_name(soup, json_ld_data),
            "country": country_name,
            "city": target_city,
            "neighborhood": self._extract_neighborhood(soup, json_ld_data),
            "address": self._extract_address(soup, json_ld_data),
            "latitude": self._extract_coordinate(json_ld_data, "latitude"),
            "longitude": self._extract_coordinate(json_ld_data, "longitude"),
            "phone": self._extract_phone(soup, json_ld_data),
            "website": self._extract_website(soup, json_ld_data),
            "email": self._extract_email(soup),
            "opening_hours": self._extract_opening_hours(json_ld_data),
            "price_range": self._extract_price_range(soup, json_ld_data),
            "cuisine": self._extract_cuisines(soup, json_ld_data),
            "services": self._extract_services(soup),
            "photos": self._extract_photos(soup, json_ld_data),
            "google_maps_url": None,
            "rating": self._extract_rating(soup, json_ld_data),
            "reviews_count": self._extract_reviews_count(soup, json_ld_data),
            "rating_distribution": self._extract_rating_distribution(soup),
            "reviews": self._extract_reviews(soup, json_ld_data),
            "tripadvisor_url": self._page.url.split("?")[0],
        }

        if data["latitude"] and data["longitude"]:
            data["google_maps_url"] = f"https://www.google.com/maps?q={data['latitude']},{data['longitude']}"
        elif data["address"] or data["name"]:
            query_str = f"{data['name']}, {data['address']}".strip(", ")
            data["google_maps_url"] = f"https://www.google.com/maps/search/?api=1&query={quote_plus(query_str)}"

        return data

    # -------------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------------

    def _extract_json_ld(self, soup: BeautifulSoup) -> Dict[str, Any]:
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            if not script.string:
                continue
            try:
                parsed = json.loads(script.string)
                items = parsed if isinstance(parsed, list) else [parsed]
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    item_type = item.get("@type", "")
                    if isinstance(item_type, list):
                        if any(t in ("Restaurant", "FoodEstablishment", "LocalBusiness") for t in item_type):
                            return item
                    elif item_type in ("Restaurant", "FoodEstablishment", "LocalBusiness"):
                        return item
            except Exception:
                continue
        return {}

    def _extract_name(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> str:
        if json_ld.get("name"):
            return str(json_ld["name"]).strip()
        h1 = soup.find("h1")
        return h1.get_text(strip=True) if h1 else ""

    def _extract_neighborhood(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> str:
        addr = json_ld.get("address", {})
        if isinstance(addr, dict) and addr.get("addressLocality"):
            return str(addr["addressLocality"]).strip()

        b_elem = soup.select_one('a[href*="GeoLocation"], a[href*="Restaurants-g"]')
        return b_elem.get_text(strip=True) if b_elem else ""

    def _extract_address(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> str:
        addr = json_ld.get("address", {})
        if isinstance(addr, dict):
            parts = [
                addr.get("streetAddress"),
                addr.get("addressLocality"),
                addr.get("addressRegion"),
                addr.get("postalCode"),
                addr.get("addressCountry"),
            ]
            clean_parts = [str(p).strip() for p in parts if p and isinstance(p, (str, int))]
            if clean_parts:
                return ", ".join(clean_parts)

        addr_elem = soup.select_one('span[class*="street-address"], a[href="#MAP"] span, button[aria-label*="Address"]')
        return addr_elem.get_text(strip=True) if addr_elem else ""

    def _extract_coordinate(self, json_ld: Dict[str, Any], key: str) -> Optional[float]:
        geo = json_ld.get("geo", {})
        if isinstance(geo, dict) and key in geo:
            try:
                return float(geo[key])
            except (ValueError, TypeError):
                return None
        return None

    def _extract_phone(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> str:
        if json_ld.get("telephone"):
            return str(json_ld["telephone"]).strip()

        phone_elem = soup.select_one('a[href^="tel:"]')
        if phone_elem:
            href = phone_elem.get("href", "")
            return href.replace("tel:", "").strip() or phone_elem.get_text(strip=True)
        return ""

    def _extract_website(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> str:
        if json_ld.get("url"):
            return str(json_ld["url"]).strip()
        web_elem = soup.select_one('a[aria-label*="Website"], a[href*="Website"]')
        return web_elem["href"] if web_elem and web_elem.has_attr("href") else ""

    def _extract_email(self, soup: BeautifulSoup) -> str:
        email_elem = soup.select_one('a[href^="mailto:"]')
        if email_elem:
            href = email_elem.get("href", "")
            return href.replace("mailto:", "").split("?")[0].strip()
        return ""

    def _extract_opening_hours(self, json_ld: Dict[str, Any]) -> List[str]:
        hours_spec = json_ld.get("openingHoursSpecification", [])
        hours_list: List[str] = []
        if isinstance(hours_spec, list):
            for spec in hours_spec:
                if isinstance(spec, dict):
                    days = spec.get("dayOfWeek", [])
                    days_str = ", ".join(days) if isinstance(days, list) else str(days)
                    opens = spec.get("opens", "")
                    closes = spec.get("closes", "")
                    if opens and closes:
                        hours_list.append(f"{days_str}: {opens} - {closes}")
        elif json_ld.get("openingHours"):
            oh = json_ld["openingHours"]
            hours_list = [str(item) for item in oh] if isinstance(oh, list) else [str(oh)]
        return hours_list

    def _extract_price_range(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> str:
        if json_ld.get("priceRange"):
            return str(json_ld["priceRange"]).strip()
        price_elem = soup.select_one('a[href*="Price"], div[aria-label*="Price"]')
        return price_elem.get_text(strip=True) if price_elem else ""

    def _extract_cuisines(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> List[str]:
        cuisines = json_ld.get("servesCuisine", [])
        if cuisines:
            return [str(c).strip() for c in cuisines] if isinstance(cuisines, list) else [str(cuisines).strip()]

        tags = soup.select('a[href*="Cuisines"]')
        return [t.get_text(strip=True) for t in tags if t.get_text(strip=True)]

    def _extract_services(self, soup: BeautifulSoup) -> List[str]:
        features = []
        for element in soup.find_all(["div", "span", "h3", "h4"]):
            text = element.get_text(strip=True).upper()
            if "FEATURES" in text or "CARACTÉRISTIQUES" in text:
                parent_or_next = element.find_next_sibling() or element.parent
                if parent_or_next:
                    feat_text = parent_or_next.get_text(strip=True)
                    if feat_text and "FEATURES" not in feat_text.upper():
                        features.extend([f.strip() for f in feat_text.split(",") if f.strip()])
                break
        return list(set(features))

    def _extract_photos(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> List[str]:
        photos: List[str] = []
        image_ld = json_ld.get("image")
        if image_ld:
            if isinstance(image_ld, list):
                for img in image_ld:
                    url = img.get("url", img) if isinstance(img, dict) else str(img)
                    if url and url not in photos:
                        photos.append(url)
            elif isinstance(image_ld, str):
                photos.append(image_ld)

        for img in soup.select('img[src*="media-cdn.tripadvisor.com"], img[data-lazyurl*="media-cdn.tripadvisor.com"]'):
            src = img.get("data-lazyurl") or img.get("src")
            if src and src not in photos:
                photos.append(src)

        return photos[:10]

    def _extract_rating(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> Optional[float]:
        agg = json_ld.get("aggregateRating", {})
        if isinstance(agg, dict) and "ratingValue" in agg:
            try:
                return float(agg["ratingValue"])
            except (ValueError, TypeError):
                pass

        rating_elem = soup.select_one('span[class*="overallRating"], svg[aria-label*="bubbles"]')
        if rating_elem:
            aria = rating_elem.get("aria-label", "") or rating_elem.get_text(strip=True)
            match = re.search(r"(\d[\.,]\d|\d)", aria)
            if match:
                try:
                    return float(match.group(1).replace(",", "."))
                except ValueError:
                    pass
        return None

    def _extract_reviews_count(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> int:
        agg = json_ld.get("aggregateRating", {})
        if isinstance(agg, dict) and "reviewCount" in agg:
            try:
                return int(agg["reviewCount"])
            except (ValueError, TypeError):
                pass

        count_elem = soup.select_one('a[href="#REVIEWS"] span, span[class*="reviewCount"]')
        if count_elem:
            digits = re.sub(r"\D", "", count_elem.get_text(strip=True))
            if digits:
                return int(digits)
        return 0

    def _extract_rating_distribution(self, soup: BeautifulSoup) -> Dict[str, int]:
        dist = {"5_star": 0, "4_star": 0, "3_star": 0, "2_star": 0, "1_star": 0}
        rows = soup.select('div[data-aria-label*="star"], div[class*="chartRow"], div[aria-label*="reviews"]')
        for row in rows:
            text = row.get_text(strip=True).lower()
            label = row.get("data-aria-label") or row.get("aria-label") or text

            star_match = re.search(r"([1-5])\s*star", label)
            count_match = re.search(r"(\d[\d,.]*)", text)

            if star_match and count_match:
                star_key = f"{star_match.group(1)}_star"
                try:
                    count_val = int(count_match.group(1).replace(",", "").replace(".", ""))
                    dist[star_key] = count_val
                except ValueError:
                    continue

        return dist

    def _extract_reviews(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> List[Dict[str, Any]]:
        reviews: List[Dict[str, Any]] = []

        ld_reviews = json_ld.get("review", [])
        if isinstance(ld_reviews, list) and ld_reviews:
            for rev in ld_reviews:
                if not isinstance(rev, dict):
                    continue
                author = rev.get("author", {})
                author_name = author.get("name", "Anonymous") if isinstance(author, dict) else str(author)

                review_rating = None
                r_obj = rev.get("reviewRating", {})
                if isinstance(r_obj, dict) and "ratingValue" in r_obj:
                    try:
                        review_rating = float(r_obj["ratingValue"])
                    except (ValueError, TypeError):
                        pass

                reviews.append({
                    "author": author_name,
                    "date": rev.get("datePublished", ""),
                    "language": "en",
                    "rating": review_rating,
                    "text": rev.get("reviewBody", ""),
                    "owner_response": None,
                })

        if reviews:
            return reviews

        review_cards = soup.select('div[data-reviewid], div[class*="review-container"], div[data-test-target="HR_CC_CARD"]')
        for card in review_cards:
            try:
                author_elem = card.select_one('a[href*="Profile"], .ui_header_link, span[class*="author"]')
                author = author_elem.get_text(strip=True) if author_elem else "Anonymous"

                date_elem = card.select_one('span[class*="ratingDate"], div[class*="date"], span[aria-label*="wrote"]')
                date_text = date_elem.get_text(strip=True) if date_elem else ""

                rating_val = None
                bubble = card.select_one('span[class*="bubble_"], svg[aria-label*="bubbles"]')
                if bubble:
                    cls_list = bubble.get("class", [])
                    for cls in cls_list:
                        if "bubble_" in cls:
                            try:
                                rating_val = float(cls.split("bubble_")[-1]) / 10.0
                            except ValueError:
                                pass
                    if rating_val is None and bubble.get("aria-label"):
                        match = re.search(r"(\d[\.,]\d|\d)", bubble["aria-label"])
                        if match:
                            try:
                                rating_val = float(match.group(1).replace(",", "."))
                            except ValueError:
                                pass

                text_elem = card.select_one('span[class*="fullText"], div[class*="entry"], div[data-test-target="review-title"] + div')
                text = text_elem.get_text(strip=True) if text_elem else ""

                response_elem = card.select_one('div[class*="mgrRspnInline"], div[class*="ownerResponse"]')
                owner_response = response_elem.get_text(strip=True) if response_elem else None

                if text:
                    reviews.append({
                        "author": author,
                        "date": date_text,
                        "language": "en",
                        "rating": rating_val,
                        "text": text,
                        "owner_response": owner_response,
                    })
            except Exception as exc:
                logger.debug("Error parsing DOM review card: %s", exc)
                continue

        return reviews


# Alias de la classe pour assurer l'importation 'from .parser import Parser' dans __init__.py
Parser = TripAdvisorParser