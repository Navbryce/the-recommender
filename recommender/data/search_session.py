from typing import Optional

from attr import dataclass

from recommender.data.business_search_request import BusinessSearchRequest


@dataclass
class SearchSession:
    id: str
    search_request: BusinessSearchRequest
    next_recommendation_id: Optional[str] = None
    seen_business_ids: [str] = []
