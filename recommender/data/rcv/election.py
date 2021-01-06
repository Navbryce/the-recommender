from __future__ import annotations
from datetime import datetime
from typing import Callable

from sqlalchemy import String, Column, DateTime, Float, Index, ForeignKey, Enum
from sqlalchemy.orm import composite, relationship, Session, load_only, Query

from recommender.data.rcv.candidate import Candidate
from recommender.data.rcv.election_status import ElectionStatus
from recommender.data.recommendation.location import Location
from recommender.db_config import DbBase

ACTIVE_ID_LENGTH = 6


class Election(DbBase):
    @staticmethod
    def get_election_by_id(
        db_session: Session,
        id: str,
        query_modifier: Callable[[Query], Query] = lambda x: x,
    ) -> Election:
        return query_modifier(db_session.query(Election)).filter_by(id=id).first()

    @staticmethod
    def get_active_election_by_active_id(
        db_session: Session,
        active_id: str,
        query_modifier: Callable[[Query], Query] = lambda x: x,
    ) -> Election:
        return (
            query_modifier(db_session.query(Election))
            .filter_by(active_id=active_id, election_completed_at=None)
            .first()
        )

    __tablename__ = "election"

    id: str = Column(String(length=36), primary_key=True)
    active_id: str = Column(String(length=ACTIVE_ID_LENGTH))
    election_status: ElectionStatus = Column(
        Enum(ElectionStatus), default=ElectionStatus.IN_CREATION, nullable=False
    )
    election_completed_at: datetime = Column(DateTime)
    election_creator_id: str = Column(
        String(length=36), ForeignKey("user.id"), primary_key=True, nullable=False
    )

    lat: float = Column(Float)
    long: float = Column(Float)
    location: Location = composite(Location, lat, long)

    candidates: [Candidate] = relationship("Candidate")

    __table_args__ = (Index("active_id", active_id, election_completed_at),)
