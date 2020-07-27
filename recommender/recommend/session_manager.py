from recommender.data.business import Business
from recommender.data.business_search_request import BusinessSearchRequest
from recommender.data.recommendation_engine_input import RecommendationEngineInput
from recommender.data.search_session import SearchSession
from recommender.recommend.recommender import Recommender


class SessionManager:
    def __init__(self, recommender: Recommender) -> None:
        super().__init__()
        self.recommender = recommender

    def new_session(self, search_request: BusinessSearchRequest) -> SearchSession:
        print('new session')

    def get_next_recommendation_for_session(self, session: SearchSession) -> Business:
        business_recommendation = self.recommender.recommend(self.get_recommendation_input_from_session(session))
        session.next_recommendation_id = business_recommendation.id
        return business_recommendation


    def get_recommendation_input_from_session(self, session: SearchSession) -> RecommendationEngineInput:
        return RecommendationEngineInput(search_request=session.searchRequest,
                                         seen_business_ids=session.seen_business_ids)
