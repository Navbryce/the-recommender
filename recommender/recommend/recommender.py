import math
import random
from logging import warning
from typing import Final

from fuzzywuzzy import fuzz

from recommender.api.utils.http_exception import ErrorCode, HttpException
from recommender.business.page import Page
from recommender.business.search_client import SearchClient
from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)
from recommender.data.recommendation.displayable_recommendation import (
    DisplayableRecommendation,
)
from recommender.data.recommendation.filterable_business import RecommendableBusiness
from recommender.data.recommendation.recommendation import Recommendation
from recommender.recommend.recommendation_engine_input import RecommendationEngineInput


class Recommender:
    __LIMIT_TO_USE: Final[int] = 20
    __MAX_FETCHES: Final[int] = 1

    def __init__(self, search_client: SearchClient):
        self._search_client = search_client

    def recommend(
        self, recommendation_input: RecommendationEngineInput
    ) -> Recommendation:
        potential_businesses_to_recommend = self.__fetch_unseen_businesses(
            recommendation_input, target_amount=20
        )
        if len(recommendation_input.search_request.search_term) == 0:
            business_to_recommend: RecommendableBusiness = potential_businesses_to_recommend[
                random.randint(0, len(potential_businesses_to_recommend) - 1)
            ]
        else:
            business_to_recommend: RecommendableBusiness = sorted(
                potential_businesses_to_recommend,
                key=lambda business: fuzz.partial_ratio(
                    recommendation_input.search_request.search_term, business.name
                ),
                reverse=True,
            )[0]
        return Recommendation(
            session_id=recommendation_input.session_id,
            business_id=business_to_recommend.id,
            distance=business_to_recommend.distance,
            business_data_for_recommendation=business_to_recommend,
        )

    def __fetch_unseen_businesses(
        self, recommendation_input: RecommendationEngineInput, target_amount
    ) -> [RecommendableBusiness]:
        seen_business_ids = recommendation_input.seen_business_ids

        potential_recommendations = []
        initial_offset = math.floor(len(seen_business_ids) / self.__LIMIT_TO_USE)
        current_page = Page(limit=self.__LIMIT_TO_USE, offset=initial_offset)
        iteration_counter = 0
        while len(potential_recommendations) < target_amount:
            if iteration_counter >= self.__MAX_FETCHES:
                break
            raw_businesses = self.__fetch_raw_businesses(
                recommendation_input.search_request, current_page
            )
            if len(raw_businesses) == 0:
                break
            seen_business_names = recommendation_input.normalized_seen_business_names
            unseen_businesses = list(
                filter(
                    lambda x: x.name.lower() not in seen_business_names, raw_businesses
                )
            )

            potential_recommendations = potential_recommendations + unseen_businesses

            current_page = current_page.next_page()
            iteration_counter += 1
        if len(potential_recommendations) == 0:
            raise HttpException(
                message="No businesses found. Try different parameters",
                error_code=ErrorCode.NO_BUSINESSES_FOUND,
            )
        elif len(potential_recommendations) < target_amount:
            warning(
                f"Target amount of {target_amount} not reached. Actual: {len(potential_recommendations)}"
            )
        return potential_recommendations

    def __fetch_raw_businesses(
        self, search_params: BusinessSearchRequest, page: Page
    ) -> [RecommendableBusiness]:
        return self._search_client.business_search(search_params, page)

    def generate_detailed_recommendation(
        self, filterable_business: RecommendableBusiness, session_id: str
    ) -> DisplayableRecommendation:
        displayable_business = self._search_client.get_displayable_business(
            filterable_business.id
        )
        return DisplayableRecommendation(
            session_id=session_id,
            business=displayable_business,
            distance=filterable_business.distance,
        )
