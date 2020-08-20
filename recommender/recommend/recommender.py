from uuid import uuid4

from recommender.data.recommendation.business_search_request import BusinessSearchRequest
from recommender.data.recommendation.displayable_recommendation import DisplayableRecommendation
from recommender.data.recommendation.filterable_business import FilterableBusiness
from recommender.recommend.recommendation_engine_input import RecommendationEngineInput
from recommender.external_api_clients.search_client import SearchClient
from recommender.external_api_clients.page import Page, FIRST_PAGE


class Recommender:
    def __init__(self, search_client: SearchClient):
        self._search_client = search_client

    def recommend(self, recommendation_input: RecommendationEngineInput) -> DisplayableRecommendation:
        potential_businesses_to_recommend = self.fetch_unseen_businesses(recommendation_input, target_amount=20)
        return self.generate_detailed_recommendation(potential_businesses_to_recommend[0])

    def fetch_unseen_businesses(self, recommendation_input: RecommendationEngineInput, target_amount) -> [FilterableBusiness]:
        seen_business_ids = recommendation_input.seen_business_ids
        potential_recommendations = []
        current_page: Page = FIRST_PAGE
        while len(potential_recommendations) < target_amount:
            raw_businesses = self.fetch_raw_businesses(recommendation_input.search_request, current_page)
            unseen_businesses = list(filter(lambda x: x.id not in seen_business_ids, raw_businesses))
            potential_recommendations = potential_recommendations + unseen_businesses

            current_page = current_page.next_page()
        return potential_recommendations

    def fetch_raw_businesses(self, search_params: BusinessSearchRequest, page: Page) -> [FilterableBusiness]:
        return self._search_client.business_search(search_params, page)

    def generate_detailed_recommendation(self, filterable_business: FilterableBusiness) -> DisplayableRecommendation:
        displayable_business = self._search_client.get_displayable_business(filterable_business.id)
        return DisplayableRecommendation(id=str(uuid4()), business=displayable_business, distance=filterable_business.distance)
