from recommender.data.business import Business
from recommender.data.business_search_request import BusinessSearchRequest
from recommender.external_api_clients.search_client import SearchClient


class Recommender:
    def __init__(self, search_client: SearchClient):
        self._search_client = search_client

    def recommend(self, req: BusinessSearchRequest) -> Business:
        possible_businesses = self._search_client.business_search(
            req.location,
            req.search_term,
            req.price_categories,
            req.categories,
            req.attributes,
            req.radius,
        )
        return possible_businesses[0]
