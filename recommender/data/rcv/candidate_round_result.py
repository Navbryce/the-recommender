from typing import Optional

from sqlalchemy import (
    Integer,
    Column,
    String,
    ForeignKey,
    PrimaryKeyConstraint,
    ForeignKeyConstraint,
    Enum,
)
from sqlalchemy.orm import relationship

from recommender.data.rcv.candidate import Candidate
from recommender.data.rcv.round_action import RoundAction


class CandidateRoundResult:
    __tablename__ = "candidate_round_result"

    election_id: str = Column(
        String(length=36), ForeignKey("election.id"), nullable=False
    )
    round_number: int = Column(Integer(), nullable=False)
    business_id: str = Column(String(length=100), nullable=False)
    number_of_rank_one_votes: int = Column(Integer(), nullable=False)

    candidate: Candidate = relationship("candidate", uselist=False)
    round_action: Optional[RoundAction] = Column(Enum(RoundAction))

    __table_args__ = (
        PrimaryKeyConstraint(election_id, round_number, business_id),
        ForeignKeyConstraint(
            [election_id, round_number], ["round.election_id", "round.round_number"]
        ),
        ForeignKeyConstraint(
            [election_id, business_id],
            ["candidate.election_id", "candidate.business_id"],
        ),
    )
