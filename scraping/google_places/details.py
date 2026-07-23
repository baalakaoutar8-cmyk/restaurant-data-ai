import requests


class PlaceDetails:

    URL = (

        "https://maps.googleapis.com/maps/api/place/details/json"

    )

    def __init__(self, api_key):

        self.api_key = api_key

    def get(self, place_id):

        params = {

            "place_id": place_id,

            "fields": (

                "name,"

                "formatted_address,"

                "formatted_phone_number,"

                "website,"

                "geometry,"

                "rating,"

                "user_ratings_total"

            ),

            "key": self.api_key,

        }

        return requests.get(

            self.URL,

            params=params,

        ).json()["result"]