from recommender.data.recommendation.displayable_recommendation import DisplayableRecommendation
from recommender.recommend.recommendation_engine_input import RecommendationEngineInput
from recommender.recommend.recommendation_repository import RecommendationRepository
from recommender.recommend.recommendation_request import RecommendationRequest
from recommender.recommend.recommender import Recommender


class RecommendationManager:
    def __init__(self, recommender: Recommender, recommendation_repository: RecommendationRepository) -> None:
        super().__init__()
        self.__recommendation_repository = recommendation_repository
        self.__recommender = recommender

    def generate_recommendation(self, request: RecommendationRequest) -> DisplayableRecommendation:
        rejected_recommendations = self.__recommendation_repository.get_recommendations(
            request.rejected_recommendation_ids)
        maybe_recommendations = self.__recommendation_repository.get_recommendations(request.maybe_recommendation_ids)
        recommendation_engine_input = RecommendationEngineInput(search_request=request.search_request,
                                                                rejected_recommendations=rejected_recommendations,
                                                                maybe_recommendations=maybe_recommendations)
        recommendation = self.__recommender.recommend(recommendation_engine_input)
        self.__recommendation_repository.insert_recommendation(recommendation)
        return recommendation
