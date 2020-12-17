from typing import Dict
from recommender.session.search_session import SearchSession
from recommender.session.session_repository import SessionRepository


class InMemorySessionRepository(SessionRepository):
    session_repository: Dict[str, SearchSession] = {}

    def get_session(self, session_id: str):
        if session_id not in self.session_repository:
            raise ValueError(f"Could not find session with id {session_id}")
        return self.session_repository[session_id].clone()

    def insert_new_session(self, session: SearchSession):
        self.session_repository[session.id] = session.clone()

    def insert_new_recommendation(self, recommendation: str):
        self.recommendation_repository[recommendation.id] = recommendation

    def get_recommendations(self, recommendation_ids: [str]) -> [str]:
        return [
            self.recommendation_repository[recommendation_id]
            for recommendation_id in recommendation_ids
        ]

    def set_current_recommendation_for_session(self, session_id: str, rec_id: str):
        self.session_repository[session_id].current_recommendation_id = rec_id

    def get_current_recommendation_id_for_session(self, session_id: str) -> str:
        return self.session_repository[session_id].current_recommendation_id

    def add_rejected_recommendation(self, session_id: str, recommendation_id: str):
        self.session_repository[session_id].rejected_recommendation_ids.append(
            recommendation_id
        )

    def add_maybe_recommendation(self, session_id: str, recommendation_id: str):
        self.session_repository[session_id].maybe_recommendation_ids.append(
            recommendation_id
        )

    def set_maybe_recommendation_to_rejected(
        self, session_id: str, recommendation_id: str
    ):
        current_session = self.session_repository[session_id]
        self.session_repository[session_id].maybe_recommendation_ids = list(
            filter(
                lambda x: x != recommendation_id,
                current_session.maybe_recommendation_ids,
            )
        )
        current_session.rejected_business_ids.append(recommendation_id)

    def clear_all_maybe_recommendations(self, session_id: str):
        self.session_repository[session_id].maybe_recommendation_ids.clear()

    def set_as_accepted_recommendation(self, session_id: str, recommendation_id: str):
        self.session_repository[
            session_id
        ].current_recommendation_id = recommendation_id
