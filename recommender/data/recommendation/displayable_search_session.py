from dataclasses import dataclass, field
from typing import Optional

from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)
from recommender.data.recommendation.displayable_recommendation import (
    DisplayableRecommendation,
)
from recommender.data.recommendation.search_session_status import SearchSessionStatus


@dataclass
class DisplayableSearchSession:
    id: str
    search_request: BusinessSearchRequest
    maybe_recommendations: [DisplayableRecommendation]
    rejected_recommendations: [DisplayableRecommendation]
    session_status: SearchSessionStatus
    accepted_recommendations: Optional[DisplayableRecommendation] = field(default_factory=list)
    current_recommendation: Optional[DisplayableRecommendation] = None
