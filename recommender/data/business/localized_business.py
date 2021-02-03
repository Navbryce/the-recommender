from dataclasses import dataclass

from recommender.data.business.displayable_business import DisplayableBusiness


@dataclass
class LocalizedBusiness:
    business: DisplayableBusiness
    distance: float