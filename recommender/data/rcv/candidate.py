from typing import Optional

from sqlalchemy import ForeignKey, String, Column, Float, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from recommender.data.auth.user import BasicUser
from recommender.data.rcv.ranking import Ranking
from recommender.data.serializable import serializable_persistence_object
from recommender.db_config import DbBase


@serializable_persistence_object
class Candidate(DbBase):
    __tablename__ = "candidate"

    nominator_id: Optional[str] = Column(String(length=36), ForeignKey(BasicUser.id))
    election_id: str = Column(
        String(length=36), ForeignKey("election.id"), nullable=False
    )
    business_id: str = Column(String(length=100), nullable=False)
    distance: float = Column(Float(), nullable=True)

    rankings: [Ranking] = relationship("Ranking")
    nominator = relationship("BasicUser", uselist=False)

    __table_args__ = (PrimaryKeyConstraint(election_id, business_id),)
