from dataclasses import dataclass
from typing import Optional

from recommender.data.serializable import serializable
from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)
from recommender.data.recommendation.displayable_recommendation import (
    DisplayableRecommendation,
)


@serializable
@dataclass
class DisplayableSearchSession:
    id: str
    search_request: BusinessSearchRequest
    maybe_recommendations: [DisplayableRecommendation]
    rejected_recommendations: [DisplayableRecommendation]
    accepted_recommendation: Optional[DisplayableRecommendation] = None
    current_recommendation: Optional[DisplayableRecommendation] = None
