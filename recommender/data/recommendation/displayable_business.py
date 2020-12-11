from dataclasses import dataclass

from recommender.data.recommendation.address import Address
from recommender.data.recommendation.displayable_category import DisplayableCategory
from recommender.data.recommendation.location import Location
from recommender.data.recommendation.price import PriceCategory
from recommender.data.serializable import Serializable


@dataclass
class DisplayableBusiness(Serializable):
    id: str
    name: str
    url: str
    image_urls: [str]
    price: PriceCategory
    rating: float

    delivery: bool
    pickup: bool
    categories: [DisplayableCategory]

    coordinates: Location
    address: Address
