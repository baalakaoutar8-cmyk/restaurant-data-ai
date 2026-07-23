"""
scraper.py

Scraper Google Places (version classique).
"""

import time

from scraping.google_places.pipeline import (
    run_google_places_pipeline,
)


class GooglePlacesScraper:

    def __init__(self, country="saudi arabia"):

        self.country = country

    # =====================================================

    def scrape_city(self, city):

        print("=" * 60)
        print(city)
        print("=" * 60)

        restaurants = run_google_places_pipeline(
            city=city,
            country=self.country,
        )

        print(
            f"{len(restaurants)} restaurants récupérés."
        )

        return restaurants

    # =====================================================

    def scrape_cities(self, cities):

        all_restaurants = []

        for city in cities:

            try:

                restaurants = self.scrape_city(city)

                all_restaurants.extend(restaurants)

                # attendre avant la ville suivante
                time.sleep(2)

            except Exception as e:

                print(f"Erreur pour {city} : {e}")

                # attendre également après une erreur 429
                time.sleep(10)

        print("=" * 60)
        print(f"TOTAL : {len(all_restaurants)} restaurants")
        print("=" * 60)

        return all_restaurants