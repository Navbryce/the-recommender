import jsonpickle

from recommender.business.page import Page
from recommender.business.search_client import SearchClient
from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)
from recommender.data.recommendation.displayable_business import DisplayableBusiness
from recommender.data.recommendation.filterable_business import RecommendableBusiness

"""
layer of indirection when caching or local storage (or multiple API clients) is implemented

(implement search client temporarily depending on whether we want additional functionality on the business manager)
"""


class BusinessManager(SearchClient):
    __search_client: SearchClient

    def __init__(self, search_client: SearchClient):
        self.__search_client = search_client

    def business_search(
        self, search_params: BusinessSearchRequest, page: Page
    ) -> [RecommendableBusiness]:
        # return iterable instead ?
        return self.__search_client.business_search(search_params, page)

    def get_displayable_business(self, business_id: str) -> DisplayableBusiness:
        business = self.__search_client.get_displayable_business(business_id)
        return business
