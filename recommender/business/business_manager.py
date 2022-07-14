import jsonpickle

from recommender.business.page import Page
from recommender.business.search_client import SearchClient
from recommender.data.business.displayable_business import DisplayableBusiness
from recommender.data.business.localized_business import LocalizedBusiness
from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)
from recommender.data.recommendation.filterable_business import RecommendableBusiness
from recommender.db_config import primary_redis_conn

"""
layer of indirection when caching or local storage (or multiple API clients) is implemented

(implement search client temporarily depending on whether we want additional functionality on the business manager)
"""

CACHE_EXPIRATION_IN_DAYS = 1
CACHE_EXPIRATION_IN_SECONDS = CACHE_EXPIRATION_IN_DAYS * 24 * 60 * 60


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
        business_cache_key = f"business:{business_id}"
        cached_business_as_string = primary_redis_conn.get(business_cache_key)
        if cached_business_as_string is not None:
            return jsonpickle.decode(cached_business_as_string)
        business = self.__search_client.get_displayable_business(business_id)
        primary_redis_conn.set(
            business_cache_key,
            jsonpickle.encode(business),
            ex=CACHE_EXPIRATION_IN_SECONDS,
        )
        return business

    def get_localized_business(self, business_id: str) -> LocalizedBusiness:
        return LocalizedBusiness(
            business=self.get_displayable_business(business_id), distance=0
        )
