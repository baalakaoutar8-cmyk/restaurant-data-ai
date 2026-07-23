"""
models.py
Modèle de données pour un restaurant.
"""
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class Restaurant:
    name: str
    city: str
    country: str
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    price_range: Optional[str] = None
    cuisine_type: Optional[str] = None
    address: Optional[str] = None
    url: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)