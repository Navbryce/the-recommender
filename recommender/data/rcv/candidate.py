from typing import Optional

from sqlalchemy import ForeignKey, String, Column, Float, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from recommender.data.rcv.ranking import Ranking
from recommender.data.serializable import serializable
from recommender.db_config import DbBase


@serializable
class Candidate(DbBase):
    __tablename__ = "candidate"

    creator_id: Optional[str] = Column(String(length=36), ForeignKey("user.id"))
    election_id: str = Column(
        String(length=36), ForeignKey("election.id"), nullable=False
    )
    business_id: str = Column(String(length=100), nullable=False)
    distance: float = Column(Float(), nullable=True)
    rankings: [Ranking] = relationship("Ranking")

    __table_args__ = (PrimaryKeyConstraint(election_id, business_id),)
