"""
parser.py

Transformation des données OpenStreetMap vers le format
standard du projet.
"""

from datetime import datetime

from scraping.common.helpers import (
    clean_text,
    clean_phone,
    clean_email,
    clean_url,
    unique_list,
)


class OSMParser:
    """
    Parse les objets OpenStreetMap.
    """

    @staticmethod
    def parse_restaurant(
        element: dict,
        country: str,
        city: str,
    ) -> dict:

        tags = element.get("tags", {})

        # Coordonnées
        if "lat" in element:
            latitude = element["lat"]
            longitude = element["lon"]

        elif "center" in element:
            latitude = element["center"]["lat"]
            longitude = element["center"]["lon"]

        else:
            latitude = None
            longitude = None

        cuisines = []

        if "cuisine" in tags:
            cuisines = [
                c.strip()
                for c in tags["cuisine"].split(";")
            ]

        services = []

        if tags.get("delivery") == "yes":
            services.append("Delivery")

        if tags.get("takeaway") == "yes":
            services.append("Takeaway")

        if tags.get("drive_through") == "yes":
            services.append("Drive Through")

        if tags.get("outdoor_seating") == "yes":
            services.append("Outdoor Seating")

        if tags.get("wheelchair") == "yes":
            services.append("Wheelchair Accessible")

        restaurant = {

            "source": "OpenStreetMap",

            "osm_type": element.get("type"),

            "osm_id": element.get("id"),

            "restaurant_id":
                f"osm_{element.get('type')}_{element.get('id')}",

            "name":
                clean_text(tags.get("name")),

            "brand":
                clean_text(tags.get("brand")),

            "operator":
                clean_text(tags.get("operator")),

            "country":
                country,

            "city":
                city,

            "district":
                clean_text(
                    tags.get("addr:suburb")
                    or tags.get("addr:district")
                ),

            "address":
                clean_text(
                    tags.get("addr:full")
                    or tags.get("addr:street")
                ),

            "postcode":
                clean_text(tags.get("addr:postcode")),

            "latitude":
                latitude,

            "longitude":
                longitude,

            "phone":
                clean_phone(tags.get("phone")),

            "website":
                clean_url(tags.get("website")),

            "email":
                clean_email(tags.get("email")),

            "opening_hours":
                clean_text(tags.get("opening_hours")),

            "cuisine_type":
                unique_list(cuisines),

            "services":
                unique_list(services),

            "price_range":
                clean_text(tags.get("price")),

            "rating":
                None,

            "review_count":
                None,

            "facebook":
                clean_url(tags.get("contact:facebook")),

            "instagram":
                clean_url(tags.get("contact:instagram")),

            "twitter":
                clean_url(tags.get("contact:twitter")),

            "payment":
                clean_text(tags.get("payment")),

            "internet_access":
                clean_text(tags.get("internet_access")),

            "smoking":
                clean_text(tags.get("smoking")),

            "reservation":
                clean_text(tags.get("reservation")),

            "photos":
                None,

            "google_maps_url":
                None,

            "created_at":
                datetime.utcnow().isoformat(),

            "raw_tags":
                tags,
        }

        return restaurant

    def parse(
        self,
        elements,
        country,
        city,
    ):
        """
        Parse une liste d'éléments OSM.
        """

        restaurants = []

        for element in elements:

            try:

                restaurant = self.parse_restaurant(
                    element,
                    country,
                    city,
                )

                restaurants.append(restaurant)

            except Exception:
                continue

        return restaurants