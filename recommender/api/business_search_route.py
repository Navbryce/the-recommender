from typing import Optional

from flask import Blueprint, request
from sqlalchemy.orm import load_only

from recommender.api.global_services import business_manager, auth_route_utils
from recommender.api.rcv_route import rcv_manager
from recommender.api.utils.auth_route_utils import AuthorizationException, AuthenticationException
from recommender.api.utils.json_content_type import json_content_type
from recommender.data.auth.user import SerializableBasicUser
from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)
from recommender.data.recommendation.displayable_recommendation import (
    DisplayableRecommendation,
)
from recommender.data.recommendation.displayable_search_session import DisplayableSearchSession
from recommender.data.recommendation.recommendation_action import RecommendationAction
from recommender.data.recommendation.search_session import SearchSession
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
@auth_route_utils.get_user_route
def new_search_session(user_maybe: Optional[SerializableBasicUser]) -> SessionCreationResponse:
    search_request = BusinessSearchRequest.from_dict(request.json['businessSearchParameters'])

    dinner_party_active_id: Optional[str] = request.json['dinnerPartyActiveId']
    if dinner_party_active_id is not None and user_maybe is None:
        # a user must be logged in to join a dinner party
        raise AuthenticationException()

    session = session_manager.new_session(search_request=search_request,
                                          dinner_party_active_id=dinner_party_active_id,
                                          user_maybe=user_maybe)
    business_recommendation: DisplayableRecommendation = session_manager.get_next_recommendation_for_session(
        session_id=session.id
    )
    return SessionCreationResponse(
        session_id=session.id,
        recommendation=business_recommendation,
        dinner_party_id=session.dinner_party_id
    )


@business_search.route("/<session_id>", methods=["GET"])
@json_content_type()
@auth_route_utils.get_user_route
def get_session(session_id: str, user_maybe: Optional[SerializableBasicUser]) -> DisplayableSearchSession:
    is_user_authorized(user_maybe, session_id)

    return session_manager.get_displayable_session(session_id)


@business_search.route("/<session_id>", methods=["POST"])
@json_content_type()
@auth_route_utils.get_user_route
def apply_recommendation_action(session_id: str, user_maybe: Optional[SerializableBasicUser]) -> Optional[DisplayableRecommendation]:
    is_user_authorized(user_maybe, session_id)

    recommendation_action_as_string = request.json["recommendationAction"]
    recommendation_id = request.json["recommendationId"]

    if recommendation_action_as_string not in RecommendationAction.__members__:
        raise ValueError(
            f"Unknown recommendation action {recommendation_action_as_string}"
        )

    recommendation_action: RecommendationAction = RecommendationAction[
        recommendation_action_as_string
    ]

    is_current = request.json["isCurrent"]
    if is_current:
        session_manager.apply_recommendation_action_to_current(
            session_id=session_id,
            current_recommendation_id=recommendation_id,
            recommendation_action=recommendation_action,
        )
        return session_manager.get_next_recommendation_for_session(session_id=session_id)
    else:
        session_manager.apply_action_to_maybe(session_id=session_id,
                                              recommendation_id=recommendation_id,
                                              recommendation_action=recommendation_action)
        return None

def is_user_authorized(user: Optional[SerializableBasicUser], session_id: str):
    db_session = DbSession()
    partial_session = SearchSession.get_session_by_id(db_session, session_id, lambda x: x.options(load_only(SearchSession.id, SearchSession.created_by_id)))
    if partial_session.created_by_id is not None and user.id != partial_session.created_by_id:
        raise AuthorizationException(f"search_session--{session_id}")



