from typing import Dict

from recommender.data.data_object import DataObject
from recommender.data.location import Location


@DataObject(["search_term", "location", "price_categories", "categories", "attributes"])
class BusinessSearchRequest:
    @staticmethod
    def from_json(json_dict: Dict):
        request = BusinessSearchRequest()
        request._search_term = json_dict["search_term"]
        request._location = Location.from_json(json_dict["location"])
        return request.build()
