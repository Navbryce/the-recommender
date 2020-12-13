from typing import Dict

from recommender.data.recommendation.recommendation import Recommendation
from recommender.recommend.recommendation_repository import RecommendationRepository


class InMemoryRecommendationRepository(RecommendationRepository):
    recommendation_repository: Dict[str, Recommendation] = {}

    def insert_recommendation(self, recommendation: Recommendation):
        self.recommendation_repository[
            self.get_flattened_id(recommendation.session_id, recommendation.business_id)
        ] = recommendation

    def get_recommendations(self, session_id: str, business_ids: [str]):
        return [
            self.recommendation_repository[
                self.get_flattened_id(session_id, business_id)
            ]
            for business_id in business_ids
        ]

    def get_flattened_id(self, session_id: str, business_id: str) -> str:
        return f"{session_id}-{business_id}"
