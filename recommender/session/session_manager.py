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
            **displayable_recommendations_dict,
        )

    def new_session(self,
                    search_request: BusinessSearchRequest,
                    dinner_party_active_id: Optional[str] = None) -> SearchSession:
        session_id = str(uuid4())

        dinner_party_id = None
        if dinner_party_active_id is not None:
            dinner_party = self.__rcv_manager.get_election_by_active_id(dinner_party_active_id)
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

    def get_first_recommendation(self, session_id) -> DisplayableRecommendation:
        db_session = DbSession()
        return self.__get_next_recommendation_for_session(
            db_session, SearchSession.get_session_by_id(db_session, session_id)
        )

    def reject_maybe_recommendation(self, session_id: str, recommendation_id: str):
        db_session = DbSession()
        current_session: SearchSession = SearchSession.get_session_by_id(
            db_session, session_id
        )

        if recommendation_id not in current_session.maybe_recommendation_ids:
            raise ValueError(
                f"Could not find a recommendation {recommendation_id} in maybe recommendations for session {session_id}"
            )

        Recommendation.get_recommendation_by_key(
            db_session, session_id, recommendation_id
        ).status = RecommendationAction.REJECT
        db_session.commit()

    def get_next_recommendation(
            self,
            session_id: str,
            current_recommendation_id: str,
            recommendation_action: RecommendationAction,
    ) -> DisplayableRecommendation:
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
        if recommendation_action == RecommendationAction.MAYBE:
            current_session.maybe_recommendations.append(current_recommendation)
            current_recommendation.status = RecommendationAction.MAYBE
        else:
            current_session.rejected_recommendations.append(current_recommendation)
            current_recommendation.status = RecommendationAction.REJECT

        db_session.commit()
        current_session.current_recommendation = None
        return self.__get_next_recommendation_for_session(db_session, current_session)

    def __get_next_recommendation_for_session(
            self, db_session: Session, search_session: SearchSession
    ):
        recommendation: Recommendation = self.__recommendation_manager.generate_new_recommendation_for_session(
            search_session
        )
        search_session.current_recommendation = recommendation
        db_session.commit()
        return self.__recommendation_manager.get_displayable_recommendation_from_recommendation(
            recommendation
        )

    def accept_recommendation(self, session_id: str, accepted_rec_id: str):
        db_session = DbSession()
        current_session: SearchSession = SearchSession.get_session_by_id(
            db_session, session_id
        )
        if (
                accepted_rec_id != current_session.current_recommendation_id
                and (current_session.is_dinner_party or accepted_rec_id not in current_session.maybe_recommendation_ids)
        ):
            raise ValueError(
                f"Unknown recommendation of id {accepted_rec_id} for session {current_session.id}"
            )

        if current_session.is_dinner_party:
            self.__accept_recommendation(db_session=db_session,
                                         current_session=current_session,
                                         accepted_rec_id=accepted_rec_id)
        else:
            self.__accept_recommendation_and_complete_session(db_session=db_session,
                                                              current_session=current_session,
                                                              accepted_rec_id=accepted_rec_id)
        db_session.commit()

    def __accept_recommendation_and_complete_session(self,
                                                     db_session: DbSession,
                                                     current_session: SearchSession,
                                                     accepted_rec_id: str):
        self.__accept_recommendation(db_session, current_session, accepted_rec_id)
        possible_recommendations_to_reject = (
                current_session.maybe_recommendation_ids
                + [current_session.current_recommendation_id]
        )
        recommendation_ids_to_reject = [
            rec_id
            for rec_id in possible_recommendations_to_reject
            if rec_id != accepted_rec_id
        ]
        for rec_id in recommendation_ids_to_reject:
            Recommendation.get_recommendation_by_key(
                db_session, current_session.id, rec_id
            ).status = RecommendationAction.REJECT
        current_session.session_status = SearchSessionStatus.COMPLETE

    def __accept_recommendation_and_add_as_candidate(self,
                                db_session: DbSession,
                                current_session: SearchSession,
                                accepted_rec_id: str):
        Recommendation.get_recommendation_by_key(
            db_session, current_session.id, accepted_rec_id
        ).status = RecommendationAction.ACCEPT
        self.__rcv_manager.add_candidate(
            active_id=current_session.dinner_party.active_id,
            business_id=accepted_rec_id,
            user_id=None
        )

    def __accept_recommendation(self,
                               db_session: DbSession,
                               current_session: SearchSession,
                               accepted_rec_id: str):
        Recommendation.get_recommendation_by_key(
            db_session, current_session.id, accepted_rec_id
        ).status = RecommendationAction.ACCEPT
