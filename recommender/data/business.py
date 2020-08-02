from dataclasses import dataclass

from recommender.data.data_object import DataObject
from recommender.data.price import PriceCategory


@dataclass
class Business:
    @classmethod
    def from_dict(cls, yelp_dict):
        id = yelp_dict["id"]
        name = yelp_dict["name"]
        url = yelp_dict["url"]
        rating = yelp_dict["rating"]
        """ 
        check is necessary because price is an optional field. We want to make sure we fetched it,
        but it doens't need to be present (None price means 'FREE') 
        """
        if "price" not in yelp_dict:
            raise ValueError("No price found")
        price_category = PriceCategory.from_api_return_value(yelp_dict["price"])
        return Business(id=id,
                        name=name,
                        url=url,
                        rating=rating,
                        price_category=price_category)

    id: str
    name: str
    url: str
    rating: str
    price_category: PriceCategory