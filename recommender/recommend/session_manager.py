from uuid import uuid4

from recommender.data.recommendation.business_search_request import BusinessSearchRequest
from recommender.data.recommendation.recommendation import Recommendation
from recommender.data.recommendation.recommendation_engine_input import RecommendationEngineInput
from recommender.data.search_session import SearchSession
from recommender.recommend.recommender import Recommender


class SessionManager:
    def __init__(self, recommender: Recommender) -> None:
        super().__init__()
        self.recommender = recommender

    def new_session(self, search_request: BusinessSearchRequest) -> SearchSession:
        session_id = str(uuid4())
        return SearchSession(id=session_id,
                             search_request=search_request)


    def get_next_recommendation_for_session(self, session: SearchSession) -> Recommendation:
        business_recommendation = self.recommender.recommend(self.get_recommendation_input_from_session(session))
        session.next_recommendation_id = business_recommendation.id
        return business_recommendation

    def get_recommendation_input_from_session(self, session: SearchSession) -> RecommendationEngineInput:
        return RecommendationEngineInput(search_request=session.search_request,
                                         seen_business_ids=session.seen_business_ids)
