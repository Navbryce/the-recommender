import os

from flask import Blueprint, request

from recommender.data.recommendation_response import RecommendationResponse
from recommender.external_api_clients.yelp_client import YelpClient
from recommender.recommend.recommender import Recommender
from recommender.recommend.session_manager import SessionManager

business_search = Blueprint("business_search", __name__)

api_key = os.environ["YELP_API_KEY"]
yelp_client: YelpClient = YelpClient(api_key)
recommender: Recommender = Recommender(yelp_client)
sessionManager: SessionManager = SessionManager(recommender)


@business_search.route("/", methods=["POST"])
def new_business_search() -> RecommendationResponse:
    print(request.get_json())
    session = sessionManager.new_session(request)
    business_recommendation = sessionManager.get_next_recommendation_for_session(session)
    return RecommendationResponse(searchSession=session, recommendation=business_recommendation)
