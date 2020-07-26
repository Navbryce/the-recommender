import os

from flask import Blueprint, request

from recommender.external_api_clients.yelp_client import YelpClient
from recommender.recommend.recommender import Recommender

business_search = Blueprint("business_search", __name__)

api_key = os.environ["YELP_API_KEY"]
yelp_client: YelpClient = YelpClient(api_key)
recommender: Recommender = Recommender(yelp_client)


@business_search.route("/", methods=["POST"])
def new_business_search():
    print(request.get_json())
    return "test"
