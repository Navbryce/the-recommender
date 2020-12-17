from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)


@dataclass
class SearchSession:
    id: str
    search_request: BusinessSearchRequest
    accepted_recommendation_id: Optional[str] = None
    current_recommendation_id: Optional[str] = None
    maybe_recommendation_ids: [str] = field(default_factory=list)
    rejected_recommendation_ids: [str] = field(default_factory=list)

    @property
    def maybe_business_ids(self) -> [str]:
        return self.maybe_recommendation_ids

    @property
    def rejected_business_ids(self) -> [str]:
        return self.rejected_recommendation_ids

    def clone(self) -> SearchSession:
        return SearchSession(**self.__dict__)
