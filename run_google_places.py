"""
Lancement du scraper Google Places
"""

from scraping.google_places.pipeline import run_google_places_pipeline



if __name__ == "__main__":

    # Ville à scraper
    city = "Casablanca"


    # Lancement pipeline
    restaurants = run_google_places_pipeline(
        city=city,
        country="BAHRAIN"
    )


    print("\n============================")
    print("SCRAPING TERMINÉ")
    print("============================")


    print(
        f"Nombre de restaurants récupérés : {len(restaurants)}"
    )


    for r in restaurants[:5]:

        print(
            "\nRestaurant :",
            r.get("name")
        )

        print(
            "Adresse :",
            r.get("address")
        )

        print(
            "Note :",
            r.get("rating")
        )