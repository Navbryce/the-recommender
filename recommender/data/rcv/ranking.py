from sqlalchemy import String, Column, ForeignKeyConstraint, Integer

from recommender.db_config import DbBase


class Ranking(DbBase):
    __tablename__ = "ranking"

    election_id: str = Column(String(length=36))
    business_id: str = Column(String(length=100))
    rank: int = Column(Integer)

    __table_args__ = ForeignKeyConstraint(
        [election_id, business_id], ["Candidate.election_id", "Candidate.business_id"]
    )
