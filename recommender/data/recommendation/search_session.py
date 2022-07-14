from __future__ import annotations

from typing import Callable, Optional

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.orm import Query, Session, relationship

from recommender.data.auth.user import BasicUser
from recommender.data.rcv.election import Election
from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)
from recommender.data.recommendation.recommendation import Recommendation
from recommender.data.recommendation.recommendation_action import RecommendationAction
from recommender.data.recommendation.search_session_status import SearchSessionStatus
from recommender.data.serializable import serializable_persistence_object
from recommender.db_config import DbBase


def generate_recommendation_join_on_status(
    status: Optional[RecommendationAction],
) -> str:
    if status is None:
        status_condition = "Recommendation.status.is_(None)"
    else:
        status_condition = f"Recommendation.status == '{status.value}'"
    return f"and_(Recommendation.session_id == SearchSession.id, {status_condition})"


@serializable_persistence_object
class SearchSession(DbBase):
    @staticmethod
    def get_session_by_id(
        db_session: Session,
        session_id: str,
        query_modifier: Callable[[Query], Query] = lambda x: x,
    ) -> Optional[SearchSession]:
        return (
            query_modifier(db_session.query(SearchSession))
            .filter_by(id=session_id)
            .first()
        )

    __tablename__ = "search_session"

    id: str = Column(String(length=36), primary_key=True)
    session_status: SearchSessionStatus = Column(
        Enum(SearchSessionStatus),
        nullable=False,
        default=SearchSessionStatus.IN_PROGRESS,
    )
    search_request: BusinessSearchRequest = relationship(
        "BusinessSearchRequest", uselist=False
    )
    dinner_party_id: Optional[str] = Column(
        String(length=36), ForeignKey("election.id"), default=None
    )
    created_by_id: Optional[str] = Column(
        String(length=36), ForeignKey(BasicUser.id), nullable=True, default=None
    )

    dinner_party: Optional[Election] = relationship("Election", uselist=False)
    created_by: Optional[BasicUser] = relationship("BasicUser", uselist=False)

    @property
    def is_complete(self) -> bool:
        return self.session_status == SearchSessionStatus.COMPLETE

    @property
    def is_dinner_party(self) -> bool:
        return self.dinner_party_id is not None

    accepted_recommendations: [Recommendation] = relationship(
        "Recommendation",
        primaryjoin=generate_recommendation_join_on_status(RecommendationAction.ACCEPT),
        uselist=True,
        viewonly=True,
    )
    current_recommendation: Optional[Recommendation] = relationship(
        "Recommendation",
        primaryjoin=generate_recommendation_join_on_status(None),
        uselist=False,
        viewonly=True,
    )
    maybe_recommendations: [Recommendation] = relationship(
        "Recommendation",
        primaryjoin=generate_recommendation_join_on_status(RecommendationAction.MAYBE),
        viewonly=True,
    )
    rejected_recommendations: [Recommendation] = relationship(
        "Recommendation",
        primaryjoin=generate_recommendation_join_on_status(RecommendationAction.REJECT),
        viewonly=True,
    )

    @property
    def current_recommendation_id(self) -> str:
        return (
            None
            if self.current_recommendation is None
            else self.current_recommendation.business_id
        )

    @property
    def accepted_recommendation_ids(self) -> [str]:
        return [
            recommendation.business_id
            for recommendation in self.accepted_recommendations
        ]

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
