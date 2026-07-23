"""
Google Places API Client

Ce module est responsable des communications avec
Google Places API (New).

Il retourne uniquement les réponses JSON de Google.
"""

import os
import requests
from dotenv import load_dotenv


load_dotenv()


class GooglePlacesAPI:

    def __init__(self):

        self.api_key = os.getenv(
            "GOOGLE_PLACES_API_KEY"
        )

        self.base_url = os.getenv(
            "GOOGLE_PLACES_BASE_URL",
            "https://places.googleapis.com/v1"
        )


        if not self.api_key:
            raise ValueError(
                "GOOGLE_PLACES_API_KEY introuvable dans .env"
            )


        self.headers = {

            "Content-Type":
                "application/json",

            "X-Goog-Api-Key":
                self.api_key
        }



    # =====================================================
    # Recherche restaurants
    # =====================================================

    def search_restaurants(
            self,
            city,
            country="saudi arabia",
            query="restaurant",
            page_size=20):


        url = (
            f"{self.base_url}/places:searchText"
        )


        body = {

            "textQuery":
                f"{query} in {city}, {country}",

            "pageSize":
                page_size
        }


        headers = self.headers.copy()


        headers["X-Goog-FieldMask"] = (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.location,"
            "places.rating,"
            "places.userRatingCount,"
            "places.types,"
            "places.businessStatus"
        )


        response = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=30
        )


        response.raise_for_status()


        return response.json()



    # =====================================================
    # Détails restaurant
    # =====================================================

    def get_place_details(
            self,
            place_id):


        url = (
            f"{self.base_url}/places/{place_id}"
        )


        headers = self.headers.copy()


        headers["X-Goog-FieldMask"] = (
            "id,"
            "displayName,"
            "formattedAddress,"
            "location,"
            "nationalPhoneNumber,"
            "websiteUri,"
            "rating,"
            "userRatingCount,"
            "priceLevel,"
            "regularOpeningHours,"
            "types,"
            "googleMapsUri,"
            "businessStatus"
        )


        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )


        response.raise_for_status()


        return response.json()



    # =====================================================
    # Test connexion
    # =====================================================

    def test_connection(self):

        try:

            self.search_restaurants(
                city=" mecca",
                country="saudi arabia",
                page_size=1
            )

            return True


        except Exception as e:

            print(e)

            return False





# =========================================================
# WRAPPERS POUR PIPELINE.PY
# =========================================================

api_client = GooglePlacesAPI()



def search_restaurants(query):

    """
    Fonction appelée par pipeline.py

    Exemple:
    query = "restaurants in Casablanca, Morocco"
    """

    # séparation ville/pays
    parts = query.split(" in ")

    if len(parts) == 2:

        city = parts[1].split(",")[0].strip()

        country = (
            parts[1].split(",")[1].strip()
            if "," in parts[1]
            else "saudi arabia"
        )

    else:

        city = query
        country = "saudi arabia"



    response = api_client.search_restaurants(
        city=city,
        country=country
    )


    return response.get(
        "places",
        []
    )





def get_place_details(place_id):

    """
    Fonction appelée par pipeline.py
    """

    return api_client.get_place_details(
        place_id
    )

if __name__ == "__main__":

    import json

    api = GooglePlacesAPI()

    response = api.search_restaurants(
        city="Riyadh",
        country="saudi arabia",
        page_size=20
    )

    print(json.dumps(response, indent=2, ensure_ascii=False))