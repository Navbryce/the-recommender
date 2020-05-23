import os

from flask import Blueprint

from recommender.data.business_search_request import BusinessSearchRequest
from recommender.external_api_clients.yelp_client import YelpClient
from recommender.recommend.recommender import Recommender

business_search = Blueprint("business_search", __name__)

api_key = os.environ["YELP_API_KEY"]
yelp_client: YelpClient = YelpClient(api_key)
recommender: Recommender = Recommender(yelp_client)


@business_search.route("/")
def test():
    business_search = {
        "location": {"lat": 39.244269, "long": -76.866268},
        "search_term": "test",
        "price_categories": ["HIGH"],
        "categories": ["a category"],
        "attributes": ["an attribute"],
        "radius": 5,
        "already_seen_businesses": [],
    }
    print(recommender.recommend(BusinessSearchRequest.from_json(business_search)))
    return "test"
