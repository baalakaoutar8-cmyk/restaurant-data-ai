"""
Parser Google Places API New

Transformation du JSON Google
vers un format intermédiaire propre.
"""


from typing import List, Dict



def parse_restaurant_results(
        results: List[Dict]
):

    restaurants = []


    for place in results:


        restaurant = {


            # ID Google
            "place_id":
                place.get("id"),



            # Nom restaurant
            "name":
                place.get(
                    "displayName",
                    {}
                ).get(
                    "text"
                ),



            # Adresse
            "address":
                place.get(
                    "formattedAddress"
                ),



            # Coordonnées GPS
            "latitude":
                place.get(
                    "location",
                    {}
                ).get(
                    "latitude"
                ),



            "longitude":
                place.get(
                    "location",
                    {}
                ).get(
                    "longitude"
                ),



            # Evaluation
            "rating":
                place.get(
                    "rating"
                ),



            # Nombre avis
            "user_ratings_total":
                place.get(
                    "userRatingCount"
                ),



            # Catégories
            "types":
                place.get(
                    "types",
                    []
                ),



            # Statut
            "business_status":
                place.get(
                    "businessStatus"
                )

        }


        restaurants.append(
            restaurant
        )


    return restaurants