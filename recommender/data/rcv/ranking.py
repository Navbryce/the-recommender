from sqlalchemy import (
    String,
    Column,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    UniqueConstraint,
    ForeignKey,
)

from recommender.db_config import DbBase


class Ranking(DbBase):
    __tablename__ = "ranking"
    user_id: str = Column(String(length=36), ForeignKey("user.id"))
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
