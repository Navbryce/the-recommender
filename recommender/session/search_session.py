from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Column
from sqlalchemy.orm import relationship, Session

from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)
from recommender.data.recommendation.recommendation import Recommendation
from recommender.data.recommendation.recommendation_action import RecommendationAction
from recommender.data.serializable import serializable
from recommender.db_config import DbBase


def generate_recommendation_join_on_status(
    status: Optional[RecommendationAction]
) -> str:
    if status is None:
        status_condition = "Recommendation.status.is_(None)"
    else:
        status_condition = f"Recommendation.status == '{status.value}'"
    return f"and_(Recommendation.session_id == SearchSession.id, {status_condition})"


@serializable
class SearchSession(DbBase):
    @staticmethod
    def get_session_by_id(db_session: Session, session_id: str) -> SearchSession:
        return db_session.query(SearchSession).filter_by(id=session_id).first()

    __tablename__ = "search_session"

    id: str = Column(String(length=36), primary_key=True)
    search_request: BusinessSearchRequest = relationship(
        "BusinessSearchRequest", uselist=False
    )
    accepted_recommendation: Optional[Recommendation] = relationship(
        "Recommendation",
        primaryjoin=generate_recommendation_join_on_status(RecommendationAction.ACCEPT),
        uselist=False,
    )
    current_recommendation: Optional[Recommendation] = relationship(
        "Recommendation",
        primaryjoin=generate_recommendation_join_on_status(None),
        uselist=False,
    )
    maybe_recommendations: [Recommendation] = relationship(
        "Recommendation",
        primaryjoin=generate_recommendation_join_on_status(RecommendationAction.MAYBE),
    )
    rejected_recommendations: [Recommendation] = relationship(
        "Recommendation",
        primaryjoin=generate_recommendation_join_on_status(RecommendationAction.REJECT),
    )

    @property
    def current_recommendation_id(self) -> str:
        return self.current_recommendation.business_id

    @property
    def accepted_recommendation_id(self) -> str:
        return self.accepted_recommendation.business_id

    @property
    def maybe_recommendation_ids(self) -> [str]:
        return [
            recommendation.business_id for recommendation in self.maybe_recommendations
        ]

    @property
    def rejected_recommendation_ids(self) -> [str]:
        return [
            recommendation.business_id
            for recommendation in self.rejected_recommendations
        ]

    def clone(self) -> SearchSession:
        return SearchSession(**self.__get_public_attributes__())
