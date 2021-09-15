from __future__ import annotations
from typing import Final, Union, List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from recommender.api.utils.http_exception import HttpException, ErrorCode
from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)
from recommender.data.recommendation.displayable_recommendation import (
    DisplayableRecommendation,
)
from recommender.data.recommendation.recommendation import Recommendation
from recommender.data.recommendation.recommendation_action import RecommendationAction
from recommender.data.recommendation.search_session_status import SearchSessionStatus
from recommender.db_config import DbSession
from recommender.rcv.rcv_manager import RCVManager
from recommender.recommend.recommendation_manager import RecommendationManager
from recommender.data.recommendation.displayable_search_session import DisplayableSearchSession
from recommender.data.recommendation.search_session import SearchSession


class SessionManager:
    __recommendation_manager: Final[RecommendationManager]
    __rcv_manager: Final[RCVManager]

    def __init__(self, recommendation_manager: RecommendationManager, rcv_manager: RCVManager) -> None:
        # init tables (after everything has been imported by the services)
        self.__recommendation_manager = recommendation_manager
        self.__rcv_manager = rcv_manager

    __RECOMMENDATION_KEYS = [
        "current_recommendation",
        "accepted_recommendations",
        "maybe_recommendations",
        "rejected_recommendations",
    ]

    def get_displayable_session(self, session_id: str) -> DisplayableSearchSession:
        db_session = DbSession()
        search_session = SearchSession.get_session_by_id(db_session, session_id)
        # parallelize
        displayable_recommendations_dict = {}
        for recommendation_key in self.__RECOMMENDATION_KEYS:
            recommendation_or_recommendations: Union[
                Recommendation, List[Recommendation]
            ] = getattr(search_session, recommendation_key)
            if not isinstance(recommendation_or_recommendations, list):
                if recommendation_or_recommendations is None:
                    continue
                displayable_recommendations_dict[
                    recommendation_key
                ] = self.__recommendation_manager.get_displayable_recommendation_from_recommendation(
                    recommendation_or_recommendations
                )
            else:
                displayable_recommendations = [
                    self.__recommendation_manager.get_displayable_recommendation_from_recommendation(
                        recommendation
                    )
                    for recommendation in recommendation_or_recommendations
                ]
                displayable_recommendations_dict[
                    recommendation_key
                ] = displayable_recommendations

        return DisplayableSearchSession(
            id=session_id,
            search_request=search_session.search_request,
            session_status=search_session.session_status,
            dinner_party_id=search_session.dinner_party_id,
            **displayable_recommendations_dict,
        )

    def new_session(self,
                    search_request: BusinessSearchRequest,
                    dinner_party_active_id: Optional[str] = None) -> SearchSession:
        session_id = str(uuid4())

        dinner_party_id = None
        if dinner_party_active_id is not None:
            dinner_party = self.__rcv_manager.get_active_election_by_active_id(dinner_party_active_id)
            if dinner_party is None:
                raise HttpException(
                    message=f"Election with active id {dinner_party_active_id} not found",
                    error_code=ErrorCode.NO_ELECTION_FOUND
                )
            dinner_party_id = dinner_party.id

        new_session = SearchSession(id=session_id, search_request=search_request, dinner_party_id=dinner_party_id)
        db_session = DbSession()
        db_session.add(new_session)
        db_session.commit()
        return new_session

    def apply_recommendation_action_to_current(
            self,
            session_id: str,
            current_recommendation_id: str,
            recommendation_action: RecommendationAction,
    ):
        db_session = DbSession()
        current_session: SearchSession = SearchSession.get_session_by_id(
            db_session, session_id
        )

        if current_recommendation_id != current_session.current_recommendation_id:
            raise ValueError(
                f"Attempting to {recommendation_action} recommendation of id {current_recommendation_id}"
                f" but current recommendation is {current_session.current_recommendation_id} for "
                f"session {current_session.id}"
            )
        current_recommendation: Recommendation = Recommendation.get_recommendation_by_key(
            db_session, session_id, current_recommendation_id
        )
        if current_recommendation is None:
            return ValueError(f"Attempting to {recommendation_action} recommendation of id {current_recommendation_id},"
                              f"but current recommendation is None. This indicates the state of the session is incorrect.")
        if recommendation_action == RecommendationAction.MAYBE:
            current_session.maybe_recommendations.append(current_recommendation)
            current_recommendation.status = RecommendationAction.MAYBE
        elif recommendation_action == RecommendationAction.REJECT:
            current_session.rejected_recommendations.append(current_recommendation)
            current_recommendation.status = RecommendationAction.REJECT
        else:
            current_session.accepted_recommendations.append(current_recommendation)
            current_recommendation.status = RecommendationAction.ACCEPT
            db_session.commit() # complete transaction so rcv_manager can add candidate for SqlLite
            if current_session.is_dinner_party:
                self.__rcv_manager.add_candidate(
                    active_id=current_session.dinner_party.active_id,
                    business_id=current_recommendation_id,
                    user_id=None
                )
            else:
                self.__complete_session(db_session=db_session,
                                        current_session=current_session)

        db_session.commit()
        current_session.current_recommendation = None

    def get_next_recommendation_for_session(
            self,
            session_id: str
    ) -> DisplayableRecommendation:
        db_session = DbSession()
        search_session: SearchSession = SearchSession.get_session_by_id(db_session, session_id)
        if search_session.current_recommendation is not None:
            raise ValueError("Cannot get a new recommendation. The search session has a current recommendation")

        if search_session.is_complete:
            return None

        recommendation: Recommendation = self.__recommendation_manager.generate_new_recommendation_for_session(
            search_session
        )
        db_session.add(recommendation)
        db_session.commit()
        return self.__recommendation_manager.get_displayable_recommendation_from_recommendation(
            recommendation
        )

    def apply_action_to_maybe(self,
                              session_id: str,
                              recommendation_id: str,
                              recommendation_action: RecommendationAction):
        db_session = DbSession()
        current_session: SearchSession = SearchSession.get_session_by_id(db_session, session_id)

        if recommendation_action == RecommendationAction.MAYBE:
            raise ValueError(f"Cannot maybe a recommendation that is already maybed")

        if current_session.is_dinner_party:
            raise ValueError("Cannot apply maybe recommendation to dinner party search session")

        if recommendation_id not in current_session.maybe_recommendation_ids:
            raise ValueError(f"Recommendation of id {recommendation_id} not in maybe recommendations")

        recommendation = Recommendation.get_recommendation_by_key(
            db_session, current_session.id, recommendation_id
        )

        recommendation.status = recommendation_action
        current_session.maybe_recommendations = [rec for rec in current_session.maybe_recommendations if
                                                 rec.business_id != recommendation_id]

        if recommendation_action == RecommendationAction.ACCEPT:
            current_session.accepted_recommendations.append(recommendation)
            recommendation.session_id = session_id  # ORM workaround
            self.__complete_session(db_session=db_session,
                                    current_session=current_session)
        elif recommendation_action == RecommendationAction.REJECT:
            current_session.rejected_recommendations.append(recommendation)
        else:
            raise ValueError(f"Unsupported operation to a maybe operation: {recommendation_action}")
        db_session.commit()

    def __complete_session(self,
                           db_session: DbSession,
                           current_session: SearchSession):
        recommendations_ids_to_reject = []
        if not current_session.is_dinner_party:
            recommendations_ids_to_reject.extend(current_session.maybe_recommendation_ids)
        if current_session.current_recommendation_id is not None:
            recommendations_ids_to_reject.append(current_session.current_recommendation_id)

        for rec_id in recommendations_ids_to_reject:
            Recommendation.get_recommendation_by_key(
                db_session, current_session.id, rec_id
            ).status = RecommendationAction.REJECT

        current_session.session_status = SearchSessionStatus.COMPLETE
