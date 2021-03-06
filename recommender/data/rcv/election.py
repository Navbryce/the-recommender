from __future__ import annotations

import array
from datetime import datetime
from typing import Callable, Dict, List

from sqlalchemy import (
    String,
    Column,
    DateTime,
    Float,
    Index,
    ForeignKey,
    Enum,
    func,
    select,
)
from sqlalchemy.orm import composite, relationship, Session, load_only, Query, aliased

from recommender.data.auth.user import BasicUser
from recommender.data.rcv.candidate import Candidate
from recommender.data.rcv.election_status import ElectionStatus
from recommender.data.rcv.ranking import Ranking
from recommender.data.rcv.round import Round
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

    @staticmethod
    def get_rankings_by_user_for_election(
        db_session: Session, election_id: str
    ) -> Dict[str, List[str]]:
        aliased_ranking_table = aliased(Ranking, name="aliased_ranking")

        user_rankings = (
            db_session.query(func.group_concat(aliased_ranking_table.business_id))
            .filter(
                aliased_ranking_table.user_id == Ranking.user_id,
                aliased_ranking_table.election_id == election_id,
            )
            .order_by(aliased_ranking_table.rank.asc())
            .correlate(Ranking)
            .as_scalar()
        )
        rankings_for_election = (
            db_session.query(Ranking.user_id, user_rankings)
            .filter(Ranking.election_id == election_id)
            .group_by(Ranking.user_id)
            .all()
        )

        return {
            user_id: rank_string.split(",")
            for user_id, rank_string in rankings_for_election
        }

    @staticmethod
    def delete_election_results_for_election(db_session: Session, election_id: str):
        db_session.query(Round).filter_by(election_id=election_id).delete()

    __tablename__ = "election"

    id: str = Column(String(length=36), primary_key=True)
    active_id: str = Column(String(length=ACTIVE_ID_LENGTH))
    election_status: ElectionStatus = Column(
        Enum(ElectionStatus), default=ElectionStatus.IN_CREATION, nullable=False
    )
    election_completed_at: datetime = Column(DateTime)
    election_creator_id: str = Column(
        String(length=36), ForeignKey(BasicUser.id), nullable=False
    )

    lat: float = Column(Float)
    long: float = Column(Float)
    location: Location = composite(Location, lat, long)

    candidates: [Candidate] = relationship("Candidate")

    __table_args__ = (Index("active_id", active_id, election_completed_at),)
