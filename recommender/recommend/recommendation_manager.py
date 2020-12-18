from recommender.data.recommendation.displayable_recommendation import (
    DisplayableRecommendation,
)
from recommender.recommend.recommendation_engine_input import RecommendationEngineInput
from recommender.recommend.recommender import Recommender
from recommender.session.search_session import SearchSession


class RecommendationManager:
    def __init__(self, recommender: Recommender) -> None:
        super().__init__()
        self.__recommender = recommender

    def generate_new_recommendation_for_session(
        self, search_session: SearchSession
    ) -> DisplayableRecommendation:
        recommendation_engine_input = RecommendationEngineInput(
            session_id=search_session.id,
            search_request=search_session.search_request,
            rejected_recommendations=search_session.rejected_recommendations,
            maybe_recommendations=search_session.maybe_recommendations,
        )
        recommendation = self.__recommender.recommend(recommendation_engine_input)
        return recommendation
