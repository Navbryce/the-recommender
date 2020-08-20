from typing import Final
from uuid import uuid4

from recommender.data.recommendation.business_search_request import BusinessSearchRequest
from recommender.data.recommendation.displayable_recommendation import DisplayableRecommendation
from recommender.data.recommendation.recommendation_action import RecommendationAction
from recommender.recommend.recommendation_engine_input import RecommendationEngineInput
from recommender.recommend.recommendation_manager import RecommendationManager
from recommender.recommend.recommendation_request import RecommendationRequest
from recommender.recommend.recommender import Recommender
from recommender.session.search_session import SearchSession
from recommender.session.session_repository import SessionRepository


class SessionManager:
    __recommendation_manager: Final[RecommendationManager]
    __session_repository: Final[SessionRepository]

    def __init__(self, recommendation_manager: RecommendationManager, session_repository: SessionRepository) -> None:
        super().__init__()
        self.__recommendation_manager = recommendation_manager
        self.__session_repository = session_repository

    def new_session(self, search_request: BusinessSearchRequest) -> SearchSession:
        session_id = str(uuid4())
        new_session = SearchSession(id=session_id,
                                    search_request=search_request)
        self.__session_repository.insert_new_session(new_session)
        return new_session

    def get_first_recommendation(self, session_id) -> DisplayableRecommendation:
        return self.__get_next_recommendation_for_session(self.__session_repository.get_session(session_id))

    def get_next_recommendation(self,
                                session_id: str,
                                current_recommendation_id: str,
                                recommendation_action: RecommendationAction) -> DisplayableRecommendation:
        current_session: SearchSession = self.__session_repository.get_session(session_id)
        if current_recommendation_id != current_session.current_recommendation_id:
            raise ValueError(f"Attempting to {recommendation_action} recommendation of id {current_recommendation_id}"
                             f" but current recommendation is {current_session.id} for "
                             f"session {current_session.current_recommendation_id}")

        if recommendation_action == RecommendationAction.MAYBE:
            self.__session_repository.add_maybe_recommendation(current_session.id, current_recommendation_id)
            current_session.maybe_recommendation_ids.append(current_recommendation_id)
        else:
            self.__session_repository.add_rejected_recommendation(current_session.id, current_recommendation_id)
            current_session.rejected_recommendation_ids.append(current_recommendation_id)

        current_session.current_recommendation = None
        return self.__get_next_recommendation_for_session(current_session)

    def __get_next_recommendation_for_session(self, session: SearchSession):
        recommendation_request = RecommendationRequest(search_request=session.search_request,
                                                       rejected_recommendation_ids=session.rejected_recommendation_ids,
                                                       maybe_recommendation_ids=session.maybe_recommendation_ids)

        business_recommendation: DisplayableRecommendation = self.__recommendation_manager.generate_recommendation(
            recommendation_request)

        self.__session_repository.set_current_recommendation_for_session(session.id, business_recommendation.id)
        session.id = business_recommendation.id
        return business_recommendation

    def accept_recommendation(self, session_id, accepted_rec_id):
        current_session = self.__session_repository.get_session(session_id)
        if accepted_rec_id is not current_session.id and accepted_rec_id not in current_session.maybe_recommendations:
            raise ValueError(f"Unknown recommendation of id {accepted_rec_id} for session {current_session.id}")

        self.__session_repository.set_as_accepted_recommendation(session_id, accepted_rec_id)

        possible_recommendations_to_reject = current_session.maybe_recommendation_ids \
            .concat([current_session.current_recommendation.id])
        recommendation_ids_to_reject = [rec_id for rec_id in possible_recommendations_to_reject if
                                        rec_id != accepted_rec_id]

        self.__session_repository.set_current_recommendation_for_session(None)
        self.__session_repository.add_rejected_recommendations(session_id, recommendation_ids_to_reject)
        self.__session_repository.clear_all_maybe_recommendations(session_id)
