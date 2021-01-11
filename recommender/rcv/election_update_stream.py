from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Final
from typing import Optional, Union

from recommender.utilities.json_encode_utilities import json_encode
from recommender.data.rcv.election_status import ElectionStatus
from recommender.utilities.notification_queue import MessageStream


class ElectionUpdateEventType(Enum):
    STATUS_CHANGED = "STATUS_CHANGED"
    CANDIDATE_ADDED = "CANDIDATE_ADDED"
    RESULTS_UPDATED = "RESULTS_UPDATED"


@dataclass
class ElectionUpdateEvent:
    type: ElectionUpdateEventType
    payload: Optional[Union[ElectionStatus, str]]


class ElectionUpdateStream(MessageStream[ElectionUpdateEvent]):
    @staticmethod
    def for_election(id: str) -> ElectionUpdateStream:
        return ElectionUpdateStream(election_id=id)

    election_id: Final[str]

    def __init__(self, election_id: str):
        super(ElectionUpdateStream, self).__init__(
            queue_name=f"election:{election_id}",
            serializer=json_encode,
            deserializer=lambda x: ElectionUpdateEvent(**json.loads(x)),
        )
        self.election_id = election_id
