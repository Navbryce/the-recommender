from sqlalchemy import (
    String,
    Column,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.orm import Session

from recommender.data.auth.user import BasicUser
from recommender.db_config import DbBase


class Ranking(DbBase):
    @staticmethod
    def delete_users_rankings_for_election(
        db_session: Session, user_id: str, election_id: str
    ):
        db_session.query(Ranking).filter_by(
            user_id=user_id, election_id=election_id
        ).delete()

    __tablename__ = "ranking"

    user_id: str = Column(String(length=36), ForeignKey(BasicUser.id))
    election_id: str = Column(String(length=36))
    business_id: str = Column(String(length=100))
    rank: int = Column(Integer)

    __table_args__ = (
        PrimaryKeyConstraint(user_id, election_id, business_id),
        UniqueConstraint(user_id, election_id, rank),
        ForeignKeyConstraint(
            [election_id, business_id],
            ["candidate.election_id", "candidate.business_id"],
        ),
    )
