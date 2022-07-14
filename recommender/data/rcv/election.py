from __future__ import annotations

from datetime import datetime
from typing import Callable, Dict, List, Optional

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Index, String, func
from sqlalchemy.orm import Query, Session, aliased, relationship

from recommender.data.auth.user import BasicUser
from recommender.data.rcv.candidate import Candidate
from recommender.data.rcv.election_status import ElectionStatus
from recommender.data.rcv.ranking import Ranking
from recommender.data.serializable import serializable_persistence_object
from recommender.db_config import DbBase

ACTIVE_ID_LENGTH = 6


@serializable_persistence_object
class Election(DbBase):
    @staticmethod
    def get_election_by_id(
        db_session: Session,
        id: str,
        query_modifier: Callable[[Query], Query] = lambda x: x,
    ) -> Optional[Election]:
        return query_modifier(db_session.query(Election)).filter_by(id=id).first()

    @staticmethod
    def update_election_by_id(db_session: Session, id: str, values: Dict[str, any]):
        db_session.query(Election).filter_by(id=id).update(
            values, synchronize_session=False
        )

    @staticmethod
    def get_active_election_by_active_id(
        db_session: Session,
        active_id: str,
        query_modifier: Callable[[Query], Query] = lambda x: x,
    ) -> Optional[Election]:
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
    election_result: str = Column("election_result", JSON)

    election_creator = relationship("BasicUser", uselist=False)
    candidates: List[Candidate] = relationship("Candidate")

    __table_args__ = (Index("active_id", active_id, election_completed_at),)
