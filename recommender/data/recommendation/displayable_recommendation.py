from dataclasses import dataclass

from recommender.data.recommendation.displayable_business import DisplayableBusiness
from recommender.data.recommendation.recommendation import Recommendation
from recommender.data.serializable import serializable


@serializable
@dataclass
class DisplayableRecommendation(Recommendation):
    __mapper_args__ = {"polymorphic_identity": "Recommendation"}
    business: DisplayableBusiness
    session_id: str
    distance: float

    def __init__(
        self, session_id: str, business: DisplayableBusiness, distance: float
    ) -> None:
        super().__init__(
            session_id=session_id, business_id=business.id, distance=distance
        )
        self.business = business

    def as_recommendation(self) -> Recommendation:
        return Recommendation(
            session_id=self.session_id,
            business_id=self.business.id,
            distance=self.distance,
        )
