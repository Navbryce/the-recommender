import json
import os
from typing import Dict

import jsonpickle as jsonpickle
from flask import Blueprint, request

from recommender.data.business_search_request import BusinessSearchRequest
from recommender.data.recommendation_response import RecommendationResponse
from recommender.external_api_clients.yelp_client import YelpClient
from recommender.recommend.recommender import Recommender
from recommender.recommend.session_manager import SessionManager

business_search = Blueprint("business_search", __name__)

api_key = os.environ["YELP_API_KEY"]
yelp_client: YelpClient = YelpClient(api_key)
recommender: Recommender = Recommender(yelp_client)
session_manager: SessionManager = SessionManager(recommender)


@business_search.route("/", methods=["POST"])
def new_business_search() -> str:
    search_request = BusinessSearchRequest.from_dict(request.json)
    session = session_manager.new_session(search_request)
    business_recommendation = session_manager.get_next_recommendation_for_session(
        session
    )
    return jsonpickle.encode(
        RecommendationResponse(
            search_session=session, recommendation=business_recommendation
        ),
        unpicklable=False,
    )
