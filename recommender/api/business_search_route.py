import os

from flask import Blueprint, request, Response

from recommender.api.json_content_type import json_content_type
from recommender.data.recommendation.business_search_request import BusinessSearchRequest
from recommender.data.recommendation.displayable_recommendation import DisplayableRecommendation
from recommender.data.session_creation_response import SessionCreationResponse
from recommender.external_api_clients.yelp_client import YelpClient
from recommender.recommend.recommender import Recommender
from recommender.session.in_memory_session_repository import InMemorySessionRepository
from recommender.session.session_manager import SessionManager

business_search = Blueprint("business_search", __name__)

api_key = os.environ["YELP_API_KEY"]
yelp_client: YelpClient = YelpClient(api_key)
recommender: Recommender = Recommender(yelp_client)
session_manager: SessionManager = SessionManager(recommender, InMemorySessionRepository())


@business_search.route("/", methods=["POST"])
@json_content_type
def new_business_search() -> SessionCreationResponse:
    search_request = BusinessSearchRequest.from_dict(request.json)
    session = session_manager.new_session(search_request)
    business_recommendation: DisplayableRecommendation = session_manager.get_next_recommendation(session_id=session.id)

    return SessionCreationResponse(
            session_id=session.id,
            recommendation=business_recommendation
        )


@business_search.route("/<session_id>", methods=["POST"])
def next_recommendation(session_id: str) -> Response:
    print(session_id)


