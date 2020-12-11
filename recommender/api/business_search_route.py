import os

from flask import Blueprint, request, Response

from recommender.api.json_content_type import json_content_type
from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)
from recommender.data.recommendation.displayable_recommendation import (
    DisplayableRecommendation,
)
from recommender.data.recommendation.recommendation_action import RecommendationAction
from recommender.data.session_creation_response import SessionCreationResponse
from recommender.external_api_clients.yelp_client import YelpClient
from recommender.recommend.in_memory_recommendation_repository import (
    InMemoryRecommendationRepository,
)
from recommender.recommend.recommendation_manager import RecommendationManager
from recommender.recommend.recommender import Recommender
from recommender.session.in_memory_session_repository import InMemorySessionRepository
from recommender.session.session_manager import SessionManager

business_search = Blueprint("business_search", __name__)

api_key = os.environ["YELP_API_KEY"]
yelp_client: YelpClient = YelpClient(api_key)
recommender: Recommender = Recommender(yelp_client)
recommendation_manager: RecommendationManager = RecommendationManager(
    recommender, InMemoryRecommendationRepository()
)
session_manager: SessionManager = SessionManager(
    recommendation_manager, InMemorySessionRepository()
)


@business_search.route("", methods=["POST"])
@json_content_type
def new_business_search() -> SessionCreationResponse:
    search_request = BusinessSearchRequest.from_dict(request.json)
    session = session_manager.new_session(search_request)
    business_recommendation: DisplayableRecommendation = session_manager.get_first_recommendation(
        session_id=session.id
    )
    return SessionCreationResponse(
        session_id=session.id, recommendation=business_recommendation
    )


@business_search.route("/<session_id>", methods=["POST"])
@json_content_type
def next_recommendation(session_id: str) -> DisplayableRecommendation:
    recommendation_action_as_string = request.json["recommendationAction"]
    current_recommendation_id = request.json["currentRecommendationId"]

    if recommendation_action_as_string not in RecommendationAction.__members__:
        raise ValueError(
            f"Unknown recommendation action {recommendation_action_as_string}"
        )

    recommendation_action: RecommendationAction = RecommendationAction[
        recommendation_action_as_string
    ]

    recommendation = session_manager.get_next_recommendation(
        session_id=session_id,
        current_recommendation_id=current_recommendation_id,
        recommendation_action=recommendation_action,
    )
    return recommendation
