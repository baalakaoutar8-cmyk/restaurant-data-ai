"""
Mapper Google Places

Transformation des données Google Places
vers le schéma global restaurant du projet.
"""


from datetime import datetime
import json



def map_restaurant(
        restaurant: dict,
        city="",
        country="kuwait"
):


    return {


        # Source
        "source":
            "Google Places",



        # Champs OpenStreetMap
        "osm_type":
            None,


        "osm_id":
            None,



        # ID interne restaurant
        "restaurant_id":
            f"google_{restaurant.get('place_id')}",



        # Informations générales

        "name":
            restaurant.get("name"),


        "brand":
            None,


        "operator":
            None,



        # Localisation

        "country":
            country,


        "city":
            city,


        "district":
            None,


        "address":
            restaurant.get("address"),


        "postcode":
            None,



        "latitude":
            restaurant.get("latitude"),


        "longitude":
            restaurant.get("longitude"),



        # Contact

        "phone":
            restaurant.get("phone"),


        "website":
            restaurant.get("website"),


        "email":
            None,



        # Services

        "opening_hours":
            restaurant.get(
                "opening_hours"
            ),


        "cuisine_type":
            extract_cuisine(
                restaurant.get("types")
            ),


        "services":
            [],



        "price_range":
            restaurant.get(
                "price_level"
            ),



        # Evaluation

        "rating":
            restaurant.get("rating"),


        "review_count":
            restaurant.get(
                "user_ratings_total"
            ),



        # Réseaux sociaux

        "facebook":
            None,


        "instagram":
            None,


        "twitter":
            None,



        # Paiement et accès

        "payment":
            None,


        "internet_access":
            None,


        "smoking":
            None,


        "reservation":
            None,



        # Photos

        "photos":
            restaurant.get(
                "photos",
                []
            ),



        # Google Maps

        "google_maps_url":
            restaurant.get(
                "google_maps_uri"
            ),



        # Date création

        "created_at":
            datetime.now()
            .isoformat(),



        # Données originales

        "raw_tags":
            json.dumps(
                restaurant,
                ensure_ascii=False
            )

    }



def map_restaurants(
        restaurants,
        city="",
        country="kuwait"
):


    return [

        map_restaurant(
            r,
            city,
            country
        )

        for r in restaurants

    ]





def extract_cuisine(types):

    """
    Conversion des types Google
    vers cuisine_type
    """

    if not types:
        return None


    mapping = {

        "cafe":
            "cafe",

        "bakery":
            "bakery",

        "meal_takeaway":
            "fast_food",

        "restaurant":
            "restaurant"

    }


    for t in types:

        if t in mapping:

            return mapping[t]


    return "restaurant"