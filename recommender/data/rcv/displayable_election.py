from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List

from recommender.data.auth.displayable_user import DisplayableUser
from recommender.data.rcv.election_status import ElectionStatus


@dataclass
class DisplayableElection:
    id: str
    active_id: str
    election_status: ElectionStatus
    candidates: [DisplayableCandidate]
    voters: Optional[List[DisplayableUser]] = None


@dataclass
class DisplayableCandidate:
    business_id: str
    name: str
    nominator_nickname: str
