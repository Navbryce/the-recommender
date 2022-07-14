from __future__ import annotations

from dataclasses import dataclass

from recommender.data.rcv.election_status import ElectionStatus


@dataclass
class DisplayableElection:
    id: str
    active_id: str
    election_status: ElectionStatus
    candidates: [DisplayableCandidate]


@dataclass
class DisplayableCandidate:
    business_id: str
    name: str
    nominator_nickname: str
