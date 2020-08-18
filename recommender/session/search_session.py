from dataclasses import dataclass, field
from typing import Optional

from recommender.data.recommendation.business_search_request import BusinessSearchRequest
from recommender.data.recommendation.recommendation import Recommendation


@dataclass
class SearchSession:
    id: str
    search_request: BusinessSearchRequest
    current_recommendation: Optional[Recommendation] = None
    rejected_recommendations: [Recommendation] = field(default_factory=list)
