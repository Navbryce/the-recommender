import os
from typing import Optional

from flask import Blueprint, request

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
from recommender.recommend.recommendation_manager import RecommendationManager
from recommender.recommend.recommender import Recommender
from recommender.session.displayable_search_session import DisplayableSearchSession
from recommender.session.session_manager import SessionManager

business_search = Blueprint("business_search", __name__)

api_key = os.environ["YELP_API_KEY"]
yelp_client: YelpClient = YelpClient(api_key)
recommender: Recommender = Recommender(yelp_client)
recommendation_manager: RecommendationManager = RecommendationManager(
    yelp_client, recommender
)
session_manager: SessionManager = SessionManager(recommendation_manager)


@business_search.route("", methods=["POST"])
@json_content_type()
def new_search_session() -> SessionCreationResponse:
    search_request = BusinessSearchRequest.from_dict(request.json)
    session = session_manager.new_session(search_request)
    business_recommendation: DisplayableRecommendation = session_manager.get_first_recommendation(
        session_id=session.id
    )
    return SessionCreationResponse(
        session_id=session.id, recommendation=business_recommendation
    )


@business_search.route("/<session_id>", methods=["GET"])
@json_content_type()
def get_session(session_id: str) -> DisplayableSearchSession:
    out = session_manager.get_displayable_session(session_id)
    return out


@business_search.route("/<session_id>", methods=["POST"])
@json_content_type()
def apply_recommendation_action(session_id: str) -> Optional[DisplayableRecommendation]:
    recommendation_action_as_string = request.json["recommendationAction"]
    recommendation_id = request.json["recommendationId"]

    if recommendation_action_as_string not in RecommendationAction.__members__:
        raise ValueError(
            f"Unknown recommendation action {recommendation_action_as_string}"
        )

    recommendation_action: RecommendationAction = RecommendationAction[
        recommendation_action_as_string
    ]

    if recommendation_action == RecommendationAction.ACCEPT:
        session_manager.accept_recommendation(session_id, recommendation_id)
        return None

    is_current = request.json["isCurrent"]
    if is_current:
        return session_manager.get_next_recommendation(
            session_id=session_id,
            current_recommendation_id=recommendation_id,
            recommendation_action=recommendation_action,
        )
    else:
        if recommendation_action == RecommendationAction.MAYBE:
            raise ValueError(
                'Cannot "Maybe" a recommendation that has already had the action applied to it'
            )
        session_manager.reject_maybe_recommendation(session_id, recommendation_id)
        return None
