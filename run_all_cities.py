from config.cities import SAUDI_ARABIA_CITIES

from scraping.google_places.scraper import GooglePlacesScraper

import time


def main():

    scraper = GooglePlacesScraper(
        country="saudi arabia"
    )

    all_restaurants = []

    for city in SAUDI_ARABIA_CITIES:

        restaurants = scraper.scrape_city(city)

        all_restaurants.extend(restaurants)

        time.sleep(3)

    print(f"Total : {len(all_restaurants)}")


if __name__ == "__main__":
    main()