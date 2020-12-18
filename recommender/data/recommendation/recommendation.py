from __future__ import annotations

from typing import Optional

from sqlalchemy import Column, String, Float, ForeignKey, Enum
from sqlalchemy.orm import Session

from recommender.data.persistence_object import PersistenceObject
from recommender.db_config import DbBase
from recommender.data.recommendation.recommendation_action import RecommendationAction


class Recommendation(DbBase, PersistenceObject):
    @staticmethod
    def get_recommendation_by_key(
        db_session: Session, session_id: str, business_id: str
    ) -> Recommendation:
        return (
            db_session.query(Recommendation)
            .filter_by(session_id=session_id, business_id=business_id)
            .first()
        )

    __tablename__ = "recommendation"

    session_id: str = Column(
        String(length=36), ForeignKey("search_session.id"), primary_key=True
    )
    business_id: str = Column(String(length=100), primary_key=True)
    distance: float = Column(Float)
    status: Optional[RecommendationAction] = Column(
        Enum(RecommendationAction), default=None
    )
