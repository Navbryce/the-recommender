from recommender.data.business import Business
from recommender.data.business_search_request import BusinessSearchRequest
from recommender.data.recommendation_engine_input import RecommendationEngineInput
from recommender.external_api_clients.search_client import SearchClient


class Recommender:
    def __init__(self, search_client: SearchClient):
        self._search_client = search_client

    def recommend(self, recommendation_input: RecommendationEngineInput) -> Business:
        req_params: BusinessSearchRequest = recommendation_input.search_request
        possible_businesses = self._search_client.business_search(
            req_params.location,
            req_params.search_term,
            req_params.price_categories,
            req_params.categories,
            req_params.attributes,
            req_params.radius,
        )
        return possible_businesses[0]
