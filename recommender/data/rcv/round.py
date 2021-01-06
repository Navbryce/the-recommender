from sqlalchemy import Column, String, ForeignKey, Integer, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from recommender.data.rcv.candidate_round_result import CandidateRoundResult
from recommender.db_config import DbBase


"""
maybe get rid of this database class
"""


class Round(DbBase):
    __tablename__ = "round"

    election_id: str = Column(String(length=36), ForeignKey("election.id"))
    round_number: int = Column(Integer())
    candidate_results: [CandidateRoundResult] = relationship("candidate_round_result")

    __table_args__ = (PrimaryKeyConstraint(election_id, round_number),)
