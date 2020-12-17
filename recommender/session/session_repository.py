from abc import ABC, abstractmethod
from typing import Union, Optional

from recommender.session.search_session import SearchSession


class SessionRepository(ABC):
    @abstractmethod
    def get_session(self, session_id: str):
        pass

    @abstractmethod
    def insert_new_session(self, session: SearchSession):
        pass

    @abstractmethod
    def insert_new_recommendation(self, recommendation: str):
        pass

    @abstractmethod
    def get_recommendations(self, recommendation_ids: [str]) -> [str]:
        pass

    @abstractmethod
    def set_current_recommendation_for_session(
        self, session_id: str, recommendation_id: Optional[str]
    ):
        pass

    @abstractmethod
    def get_current_recommendation_id_for_session(self, session_id: str) -> str:
        pass

    @abstractmethod
    def add_rejected_recommendation(self, session_id: str, recommendation_id: str):
        pass

    @abstractmethod
    def add_maybe_recommendation(self, session_id: str, recommendation_id: str):
        pass

    @abstractmethod
    def set_maybe_recommendation_to_rejected(
        self, session_id: str, recommendation_id: str
    ):
        pass

    @abstractmethod
    def clear_all_maybe_recommendations(self, session_id: str):
        pass

    @abstractmethod
    def set_as_accepted_recommendation(self, session_id: str, recommendation_id: str):
        pass

    def add_rejected_recommendations(self, session_id: str, recommendation_ids: [str]):
        for recommendation_id in recommendation_ids:
            self.add_rejected_recommendation(session_id, recommendation_id)
