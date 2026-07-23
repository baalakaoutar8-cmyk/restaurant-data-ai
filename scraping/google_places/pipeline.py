"""
pipeline.py

Pipeline complet Google Places

Flux :
API -> Parser -> Mapper -> Details -> Storage
"""

import time

from scraping.google_places.api import (
    search_restaurants,
    get_place_details,
)

from scraping.google_places.parser import (
    parse_restaurant_results,
)

from scraping.google_places.mapper import (
    map_restaurants,
)

from scraping.google_places.storage import (
    save_restaurants,
)


# ============================================================
# Pipeline principal
# ============================================================

def run_google_places_pipeline(
    city,
    country="morocco",
):

    print("\n" + "=" * 60)
    print(f"Recherche restaurants : {city}, {country}")
    print("=" * 60)

    # =====================================================
    # 1. Recherche
    # =====================================================

    query = f"restaurants in {city}, {country}"

    try:
        raw_results = search_restaurants(query)
    except Exception as e:
        print(f"Erreur lors de la recherche initiale : {e}")
        raw_results = []

    if not raw_results:
        print(f"Aucun restaurant trouvé pour : {query}")
        return []

    print(
        f"Restaurants trouvés : {len(raw_results)}"
    )

    # =====================================================
    # 2. Parsing
    # =====================================================

    parsed_data = parse_restaurant_results(
        raw_results
    )

    print("Parsing terminé")

    # =====================================================
    # 3. Mapping
    # =====================================================

    restaurants = map_restaurants(
        parsed_data
    )

    print("Mapping terminé")

    # =====================================================
    # 4. Place Details
    # =====================================================

    detailed_restaurants = []

    print(
        f"Récupération des détails ({len(restaurants)} restaurants)..."
    )

    for i, restaurant in enumerate(restaurants, start=1):

        place_id = restaurant.get("id") or restaurant.get("place_id")

        if not place_id:
            detailed_restaurants.append(
                restaurant
            )
            continue

        try:
            details = get_place_details(
                place_id
            )

            if isinstance(details, dict):
                # On évite d'écraser des valeurs existantes par du None
                cleaned_details = {k: v for k, v in details.items() if v is not None}
                restaurant.update(cleaned_details)

        except Exception as e:

            print(
                f"[{i}/{len(restaurants)}] "
                f"Erreur Details ({place_id}) : {e}"
            )

        detailed_restaurants.append(
            restaurant
        )

        # évite le 429 / respect du quota d'appels API
        time.sleep(0.35)

    print("Détails récupérés")

    # =====================================================
    # 5. Sauvegarde
    # =====================================================

    if detailed_restaurants:
        save_restaurants(
            detailed_restaurants,
            city
        )

        print(
            f"{city} sauvegardé ({len(detailed_restaurants)} restaurants)"
        )
    else:
        print(f"Aucune donnée à sauvegarder pour {city}.")

    return detailed_restaurants


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    restaurants = run_google_places_pipeline(
        city="Casablanca",
        country="Morocco",
    )

    print(
        f"\nTotal final : {len(restaurants)} restaurants"
    )