from __future__ import annotations
from typing import Final, Union, List
from uuid import uuid4

from sqlalchemy.orm import Session

from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)
from recommender.data.recommendation.displayable_recommendation import (
    DisplayableRecommendation,
)
from recommender.data.recommendation.recommendation import Recommendation
from recommender.data.recommendation.recommendation_action import RecommendationAction
from recommender.db_config import DbSession, engine, DbBase
from recommender.recommend.recommendation_manager import RecommendationManager
from recommender.session.displayable_search_session import DisplayableSearchSession
from recommender.session.search_session import SearchSession


class SessionManager:
    __recommendation_manager: Final[RecommendationManager]

    def __init__(self, recommendation_manager: RecommendationManager) -> None:
        # init tables (after everything has been imported by the services)
        self.__recommendation_manager = recommendation_manager

    __RECOMMENDATION_KEYS = [
        "current_recommendation",
        "accepted_recommendation",
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
            **displayable_recommendations_dict,
        )

    def new_session(self, search_request: BusinessSearchRequest) -> SearchSession:
        session_id = str(uuid4())
        new_session = SearchSession(id=session_id, search_request=search_request)
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
        displayable_business_recommendation: DisplayableRecommendation = self.__recommendation_manager.generate_new_recommendation_for_session(
            search_session
        )
        search_session.current_recommendation = (
            displayable_business_recommendation.as_recommendation()
        )
        db_session.commit()
        return displayable_business_recommendation

    def accept_recommendation(self, session_id, accepted_rec_id):
        db_session = DbSession()
        current_session: SearchSession = SearchSession.get_session_by_id(
            db_session, session_id
        )

        if (
            accepted_rec_id != current_session.current_recommendation_id
            and accepted_rec_id not in current_session.maybe_recommendation_ids
        ):
            raise ValueError(
                f"Unknown recommendation of id {accepted_rec_id} for session {current_session.id}"
            )

        Recommendation.get_recommendation_by_key(
            db_session, session_id, accepted_rec_id
        ).status = RecommendationAction.ACCEPT

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
                db_session, session_id, rec_id
            ).status = RecommendationAction.REJECT

        db_session.commit()
