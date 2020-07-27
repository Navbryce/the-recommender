from typing import Dict, TypeVar

from recommender.data.data_object import DataObject
from recommender.data.location import Location
from recommender.data.price import PriceCategory


@DataObject(
    [
        "search_term",
        "location",
        "price_categories",
        "categories",
        "attributes",
        "radius",
        "rejected_businesses",
    ]
)
class BusinessSearchRequest:
    @staticmethod
    def from_json(json_dict: Dict):
        request = BusinessSearchRequest()
        request._search_term = json_dict["search_term"]
        request._location = Location.from_json(json_dict["location"])
        request._price_categories = [
            PriceCategory.from_name(category_name)
            for category_name in json_dict["price_categories"]
        ]
        request._categories = json_dict["categories"]
        request._attributes = json_dict["attributes"]
        request._radius = json_dict["radius"]
        request._already_seen_businesses = json_dict["rejected_businesses"]
        return request.build()
