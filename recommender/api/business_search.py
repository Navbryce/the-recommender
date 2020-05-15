import os

from flask import Blueprint

from recommender.data.location import Location
from recommender.external_api_clients.yelp_client import YelpClient

business_search = Blueprint("business_search", __name__)

api_key = os.environ["YELP_API_KEY"]
yelp_client: YelpClient = YelpClient(api_key)


@business_search.route("/")
def test():
    print(yelp_client.businesses_search(Location(39.244269, -76.866268)))
    return "test"
