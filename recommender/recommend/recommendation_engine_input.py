from dataclasses import dataclass, field

from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)
from recommender.data.recommendation.recommendation import Recommendation


@dataclass
class RecommendationEngineInput:
    session_id: str
    rejected_recommendations: [Recommendation]
    maybe_recommendations: [Recommendation]
    accepted_recommendations: [Recommendation]
    search_request: BusinessSearchRequest

    @property
    def rejected_business_ids(self):
        return [
            recommendation.business_id
            for recommendation in self.rejected_recommendations
        ]

    @property
    def maybe_business_ids(self):
        return [
            recommendation.business_id for recommendation in self.maybe_recommendations
        ]


    @property
    def accepted_recommendation_ids(self):
        return [
            recommendation.business_id for recommendation in self.accepted_recommendations
        ]

    @property
    def seen_business_ids(self):
        return self.rejected_business_ids + self.maybe_business_ids + self.accepted_recommendation_ids

    @property
    def normalized_seen_business_names(self):
        return set(
            [
                recommendation.business_data_for_recommendation.name.lower()
                for recommendation in self.rejected_recommendations
                + self.maybe_recommendations + self.accepted_recommendations
            ]
        )
