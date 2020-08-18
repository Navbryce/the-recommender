from abc import ABC, abstractmethod

from recommender.data.recommendation.recommendation import Recommendation
from recommender.session.search_session import SearchSession


class SessionRepository(ABC):
    @abstractmethod
    def get_session(self, session_id: str):
        pass

    @abstractmethod
    def insert_new_session(self, session: SearchSession):
        pass

    @abstractmethod
    def set_current_recommendation_for_session(self, session_id: str, recommendation: Recommendation):
        pass

    @abstractmethod
    def get_current_recommendation_for_session(self, session_id: str) -> Recommendation:
        pass

    @abstractmethod
    def add_rejected_recommendation(self, session_id: str, recommendation_id: str):
        pass

