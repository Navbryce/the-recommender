from recommender.data.recommendation.displayable_recommendation import (
    DisplayableRecommendation,
)
from recommender.data.recommendation.recommendation import Recommendation
from recommender.external_api_clients.search_client import SearchClient
from recommender.recommend.recommendation_engine_input import RecommendationEngineInput
from recommender.recommend.recommender import Recommender
from recommender.session.search_session import SearchSession


class RecommendationManager:
    def __init__(self, search_client: SearchClient, recommender: Recommender) -> None:
        super().__init__()
        self.__recommender = recommender
        self.__search_client = search_client

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
        return self.get_displayable_recommendation_from_recommendation(recommendation)

    def get_displayable_recommendation_from_recommendation(
        self, recommendation: Recommendation
    ) -> DisplayableRecommendation:
        displayable_business = self.__search_client.get_displayable_business(
            recommendation.business_id
        )
        return DisplayableRecommendation(
            session_id=recommendation.session_id,
            business=displayable_business,
            distance=recommendation.distance,
        )