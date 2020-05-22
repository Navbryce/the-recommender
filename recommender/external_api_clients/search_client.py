from abc import ABC, abstractmethod

from recommender.data.business import Business
from recommender.data.location import Location
from recommender.data.price import PriceCategory


class SearchClient(ABC):
    @abstractmethod
    def business_search(
        self,
        location: Location,
        search_term: str,
        price_categories: [PriceCategory],
        categories: [str],
        attributes: [str],
        radius: int,
    ) -> [Business]:
        ...
