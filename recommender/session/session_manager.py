from typing import Optional, Final
from uuid import uuid4

from recommender.data.recommendation.business_search_request import BusinessSearchRequest
from recommender.data.recommendation.displayable_recommendation import DisplayableRecommendation
from recommender.data.recommendation.recommendation_engine_input import RecommendationEngineInput
from recommender.recommend.recommender import Recommender
from recommender.session.search_session import SearchSession
from recommender.session.session_repository import SessionRepository


class SessionManager:
    __recommender: Final[Recommender]
    __session_repository: Final[SessionRepository]

    def __init__(self, recommender: Recommender, session_repository: SessionRepository) -> None:
        super().__init__()
        self.__recommender = recommender
        self.__session_repository = session_repository

    def new_session(self, search_request: BusinessSearchRequest) -> SearchSession:
        session_id = str(uuid4())
        new_session = SearchSession(id=session_id,
                                    search_request=search_request)
        self.__session_repository.insert_new_session(new_session)
        return new_session

    def get_next_recommendation(self,
                                session_id: str,
                                current_recommendation_id: Optional[str] = None) -> DisplayableRecommendation:
        current_session: SearchSession = self.__session_repository.get_session(session_id)

        rejected_recommendations = current_session.rejected_recommendations
        if current_recommendation_id is not None:
            self.__reject_recommendation(current_session, current_recommendation_id)
            rejected_recommendations.append(current_session.rejected_recommendations)

        return self.__get_next_recommendation_for_session(current_session.id, current_session.search_request, rejected_recommendations)

    def __reject_recommendation(self, current_session: SearchSession, recommendation_to_reject_id: str):
        if current_session.current_recommendation.id != recommendation_to_reject_id:
            raise ValueError(f"Attempting to reject recommendation of id {recommendation_to_reject_id} but current "
                             f"recommendation is {current_session.current_recommendation} for "
                             f"session {current_session.id}")
        self.__session_repository.add_rejected_recommendation(current_session.current_recommendation)

    def __get_next_recommendation_for_session(self,
                                              session_id: str,
                                              search_request: BusinessSearchRequest,
                                              seen_business_ids: [str]) -> DisplayableRecommendation:
        recommendation_engine_input = RecommendationEngineInput(search_request=search_request,
                                                                seen_business_ids=seen_business_ids)
        business_recommendation: DisplayableRecommendation = self.__recommender.recommend(recommendation_engine_input)
        self.__session_repository.set_current_recommendation_for_session(session_id, business_recommendation)
        return business_recommendation
