from dataclasses import dataclass

from recommender.data.recommendation.displayable_business import DisplayableBusiness
from recommender.data.recommendation.recommendation import Recommendation


@dataclass
class DisplayableRecommendation(Recommendation):
    business: DisplayableBusiness

    def __init__(self, id: str, business: DisplayableBusiness, distance: float) -> None:
        super().__init__(id=id, business_id=business.id, distance=distance)
        self.business = business

