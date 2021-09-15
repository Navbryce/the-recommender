from dataclasses import dataclass

from recommender.data.rcv.election_status import ElectionStatus


@dataclass
class ElectionMetadataResponse:
    id: str
    active_id: str
    election_status: ElectionStatus
