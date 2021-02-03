from dataclasses import dataclass

from recommender.data.business.displayable_business import DisplayableBusiness
from recommender.data.serializable import serializable_persistence_object


@serializable_persistence_object
@dataclass
class DisplayableRecommendation:
    business: DisplayableBusiness
    session_id: str
    business_id: str
    distance: float

    def __init__(self, business: DisplayableBusiness, session_id: str, distance: float):
        self.business = business
        self.session_id = session_id
        self.distance = distance
        self.business_id = business.id
