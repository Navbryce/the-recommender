from dataclasses import dataclass

from recommender.data.recommendation.business_search_request import BusinessSearchRequest


@dataclass
class RecommendationRequest:
    search_request: BusinessSearchRequest
    maybe_recommendation_ids: [str]
    rejected_recommendation_ids: [str]
