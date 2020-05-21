from typing import Dict, TypeVar

from recommender.data.data_object import DataObject
from recommender.data.location import Location
from recommender.data.price import PriceCategory

T = TypeVar("T")


@DataObject(
    [
        "search_term",
        "location",
        "price_categories",
        "categories",
        "attributes",
        "radius",
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
        return request.build()

    def array_to_search_string(values_array: [T]) -> str:
        return ", ".join(values_array)
