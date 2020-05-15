from recommender.data.data_object import DataObject
from recommender.data.price import PriceCategory


class Business(object):
    @staticmethod
    def from_dict(yelp_dict):
        business = Business()
        business._id = yelp_dict["id"]
        business._name = yelp_dict["name"]
        business._url = yelp_dict["url"]
        business._rating = yelp_dict["rating"]
        """ 
        check is necessary because price is an optional field. We want to make sure we fetched it,
        but it doens't need to be present (None price means 'FREE') 
        """
        if "price" not in yelp_dict:
            raise ValueError("No price found")
        business._priceCategory = PriceCategory.from_category_string(yelp_dict["price"])
        return business.build()

    @DataObject(["id", "name", "url", "rating", "priceCategory"])
    def __new__(cls, *args, **kwargs):
        pass
