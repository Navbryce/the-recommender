from abc import ABC, abstractmethod

from recommender.data.recommendation.recommendation import Recommendation


class RecommendationRepository(ABC):
    @abstractmethod
    def insert_recommendation(self, recommendation: Recommendation):
        pass

    @abstractmethod
    def get_recommendations(self, recommendation_ids: [str]):
        pass