from recommender.data.data_object import DataObject


class Business(object):
    @staticmethod
    def from_dict(yelp_dict):
        business = Business()
        business._id = yelp_dict["id"]
        business._name = yelp_dict["name"]
        business._url = yelp_dict["url"]
        business._rating = yelp_dict["rating"]
        return business.build()

    @DataObject(["id", "name", "url", "rating"])
    def __new__(cls, *args, **kwargs):
        pass
