from typing import Dict

from recommender.data.recommendation.recommendation import Recommendation
from recommender.session.search_session import SearchSession
from recommender.session.session_repository import SessionRepository


class InMemorySessionRepository(SessionRepository):
    repository: Dict[str, SearchSession] = {}

    def get_session(self, session_id: str):
        if session_id not in self.repository:
            raise ValueError(f"Could not find session with id {session_id}")
        return self.repository[session_id]

    def insert_new_session(self, session: SearchSession):
        self.repository[session.id] = session

    def set_current_recommendation_for_session(self, session_id: str, recommendation: Recommendation):
        self.repository[session_id].current_recommendation = recommendation

    def get_current_recommendation_for_session(self, session_id: str) -> Recommendation:
        return self.repository[session_id].current_recommendation

    def add_rejected_recommendation(self, session_id: str, recommendation: Recommendation):
        self.repository[session_id].rejected_recommendations.append(session_id)