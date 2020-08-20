from abc import ABC, abstractmethod

from recommender.data.recommendation.business_search_request import BusinessSearchRequest
from recommender.data.recommendation.displayable_business import DisplayableBusiness
from recommender.data.recommendation.filterable_business import FilterableBusiness
from recommender.external_api_clients.page import Page


class SearchClient(ABC):
    @abstractmethod
    def business_search(
        self,
        search_params: BusinessSearchRequest,
        page: Page
    ) -> [FilterableBusiness]:
        pass

    @abstractmethod
    def get_displayable_business(self, business_id: str) -> DisplayableBusiness:
        pass
