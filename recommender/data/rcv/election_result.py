from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

from recommender.data.rcv.round_action import RoundAction
from recommender.utilities.json_encode_utilities import NoNormalizationDict


@dataclass
class CandidateRoundResult:
    number_of_rank_one_votes: int
    round_action: Optional[RoundAction]


ElectionRound = Dict[str, CandidateRoundResult]


@dataclass
class ElectionResult:
    rounds: [ElectionRound]
    calculated_at: float = field(
        default_factory=datetime.now
    )  # calculated_at is a POSIX timestamp


@dataclass
class DisplayableElectionResult:
    @staticmethod
    def from_election_result(results: ElectionResult) -> DisplayableElectionResult:
        return DisplayableElectionResult(
            rounds=[NoNormalizationDict(round) for round in results.rounds],
            calculated_at=results.calculated_at,
        )

    rounds: [NoNormalizationDict[str, CandidateRoundResult]]
    calculated_at: float
