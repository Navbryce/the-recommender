from dataclasses import dataclass
from typing import Dict, TypeVar

from recommender.data.data_object import DataObject
from recommender.data.location import Location
from recommender.data.price import PriceCategory

@dataclass
class BusinessSearchRequest:
    @classmethod
    def from_dict(cls, json_dict: Dict):
        search_term = json_dict.get("search_term", "")
        location = Location.from_json(json_dict["location"])
        price_categories = [
            PriceCategory.from_name(category_name) for category_name in json_dict.get("price_categories", [])
        ]
        categories = json_dict.get("categories", [])
        attributes = json_dict.get("attributes", [])
        radius = json_dict["radius"]
        return BusinessSearchRequest(search_term=search_term,
                                     location=location,
                                     price_categories=price_categories,
                                     categories=categories,
                                     attributes=attributes,
                                     radius=radius)

    search_term: str
    location: Location
    price_categories: [PriceCategory]
    categories: [str]
    attributes: [str]
    radius: float
