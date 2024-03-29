from __future__ import annotations

from dataclasses import dataclass

from recommender.data.business.address import Address
from recommender.data.recommendation.displayable_category import DisplayableCategory
from recommender.data.recommendation.location import Location
from recommender.data.recommendation.price import PriceCategory
from recommender.data.serializable import serializable_persistence_object


@serializable_persistence_object
@dataclass
class DisplayableBusiness:
    id: str
    name: str
    url: str
    image_urls: [str]
    price: PriceCategory
    rating: float
    rating_count: int

    delivery: bool
    pickup: bool
    categories: [DisplayableCategory]

    coordinates: Location
    address: Address
