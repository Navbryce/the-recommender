from recommender.data.recommendation.business_search_request import BusinessSearchRequest
from recommender.data.recommendation.filterable_business import FilterableBusiness
from recommender.data.recommendation.recommendation import Recommendation
from recommender.data.recommendation.recommendation_engine_input import RecommendationEngineInput
from recommender.external_api_clients.search_client import SearchClient


class Recommender:
    def __init__(self, search_client: SearchClient):
        self._search_client = search_client

    def recommend(self, recommendation_input: RecommendationEngineInput) -> Recommendation:
        req_params: BusinessSearchRequest = recommendation_input.search_request
        possible_businesses = self._search_client.business_search(
            req_params
        )
        return self.generate_detailed_recommendation(possible_businesses[0])

    def generate_detailed_recommendation(self, filterable_business: FilterableBusiness) -> Recommendation:
        displayable_business = self._search_client.get_displayable_business(filterable_business.id)
        return Recommendation(business=displayable_business, distance=filterable_business.distance)
