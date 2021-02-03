from typing import Optional

from flask import Blueprint, request

from recommender.api.global_services import business_manager
from recommender.api.rcv_route import rcv_manager
from recommender.api.utils.http_exception import HttpException, ErrorCode
from recommender.api.utils.json_content_type import json_content_type
from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)
from recommender.data.recommendation.displayable_recommendation import (
    DisplayableRecommendation,
)
from recommender.data.recommendation.displayable_search_session import DisplayableSearchSession
from recommender.data.recommendation.recommendation_action import RecommendationAction
from recommender.data.session_creation_response import SessionCreationResponse
from recommender.db_config import DbSession
from recommender.recommend.recommendation_manager import RecommendationManager
from recommender.recommend.recommender import Recommender
from recommender.session.session_manager import SessionManager

business_search = Blueprint("business_search", __name__)

recommender: Recommender = Recommender(business_manager)
recommendation_manager: RecommendationManager = RecommendationManager(
    business_manager, recommender
)
session_manager: SessionManager = SessionManager(recommendation_manager, rcv_manager)


@business_search.route("", methods=["POST"])
@json_content_type()
def new_search_session() -> SessionCreationResponse:
    search_request = BusinessSearchRequest.from_dict(request.json['businessSearchParameters'])

    dinner_party_active_id: Optional[str] = request.json['dinnerPartyActiveId']
    session = session_manager.new_session(search_request, dinner_party_active_id=dinner_party_active_id)
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
