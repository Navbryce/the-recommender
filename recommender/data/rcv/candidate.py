from sqlalchemy import ForeignKey, String, Column, PrimaryKeyConstraint

from recommender.db_config import DbBase


class Candidate(DbBase):
    __tablename__ = "candidate"

    election_id: str = Column(String(length=36), ForeignKey("election.id"))
    business_id: str = Column(String(length=100))
    distance: float = Column(float, nullable=True)

    __table_args__ = PrimaryKeyConstraint([election_id, business_id])
