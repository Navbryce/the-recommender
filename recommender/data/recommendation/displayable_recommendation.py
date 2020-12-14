from dataclasses import dataclass

from recommender.data.recommendation.displayable_business import DisplayableBusiness
from recommender.data.recommendation.recommendation import Recommendation
from recommender.data.serializable import Serializable


@dataclass
class DisplayableRecommendation(Recommendation, Serializable):
    business: DisplayableBusiness

    def __init__(
        self, session_id: str, business: DisplayableBusiness, distance: float
    ) -> None:
        super().__init__(
            session_id=session_id, business_id=business.id, distance=distance
        )
        self.business = business
