from dataclasses import dataclass

from recommender.data.business_search_request import BusinessSearchRequest


@dataclass
class RecommendationEngineInput:
    seen_business_ids: [str]
    search_request: BusinessSearchRequest
