from __future__ import annotations

from typing import Optional

from sqlalchemy import Column, String, Float, ForeignKey, Enum, PickleType
from sqlalchemy.orm import Session

from recommender.data.recommendation.filterable_business import RecommendableBusiness
from recommender.db_config import DbBase
from recommender.data.recommendation.recommendation_action import RecommendationAction


class Recommendation(DbBase):
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
    distance: float = Column(Float())
    status: Optional[RecommendationAction] = Column(
        Enum(RecommendationAction), default=None
    )

    """ 
    currently store the information used to determine if a business can be recommended with the 
    recommendation (in case the business changes with time)
    """
    business_data_for_recommendation: RecommendableBusiness = Column(
        PickleType, nullable=False
    )
