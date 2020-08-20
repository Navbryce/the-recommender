from typing import Dict

from recommender.data.recommendation.recommendation import Recommendation
from recommender.recommend.recommendation_repository import RecommendationRepository


class InMemoryRecommendationRepository(RecommendationRepository):
    recommendation_repository: Dict[str, Recommendation] = {}

    def insert_recommendation(self, recommendation: Recommendation):
        self.recommendation_repository[recommendation.id] = recommendation

    def get_recommendations(self, recommendation_ids: [str]):
        return [self.recommendation_repository[recommendation_id] for recommendation_id in recommendation_ids]

