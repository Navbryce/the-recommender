from datetime import datetime
from enum import Enum

from sqlalchemy import String, Column, DateTime, Float, Index
from sqlalchemy.orm import composite, relationship

from recommender.data.rcv.candidate import Candidate
from recommender.data.rcv.election_status import ElectionStatus
from recommender.data.recommendation.location import Location
from recommender.db_config import DbBase


class Election(DbBase):
    __tablename__ = "election"

    id: str = Column(String(length=36), primary_key=True)
    active_id: str = Column(String(length=6))
    election_status: ElectionStatus = Column(
        Enum(ElectionStatus), default=ElectionStatus.ACTIVE
    )
    election_completed_at: datetime = Column(DateTime)

    lat: float = Column(Float)
    long: float = Column(Float)
    location: Location = composite(Location, lat, long)

    candidates: [Candidate] = relationship("Candidate")

    __table_args__ = Index("active_id", active_id, election_completed_at)
