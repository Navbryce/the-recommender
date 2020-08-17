from dataclasses import dataclass

from recommender.data.recommendation.displayable_business import DisplayableBusiness

@dataclass
class Recommendation:
    business: DisplayableBusiness
    distance: float

    @property
    def id(self):
        return self.business.id