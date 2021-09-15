from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Final, Dict
from typing import Optional, Union

from recommender.api.utils.server_sent_event import ServerSentEvent
from recommender.utilities.json_encode_utilities import json_encode
from recommender.data.rcv.election_status import ElectionStatus
from recommender.utilities.notification_queue import MessageStream


class ElectionUpdateEventType(Enum):
    STATUS_CHANGED = "STATUS_CHANGED"
    CANDIDATE_ADDED = "CANDIDATE_ADDED"
    RESULTS_UPDATED = "RESULTS_UPDATED"


class CandidateAddedEvent(ServerSentEvent[Dict]):
    business_id: str
    name: str

    def __init__(self, business_id: str, name: str):
        super(CandidateAddedEvent, self).__init__(
            id=f"{ElectionUpdateEventType.CANDIDATE_ADDED.value}-{business_id}",
            type=ElectionUpdateEventType.CANDIDATE_ADDED.value,
            data={"business_id": business_id, "name": name}
        )

class ElectionUpdateStream(MessageStream[Union[ServerSentEvent[Union[ElectionStatus, None]], CandidateAddedEvent]]):
    @staticmethod
    def for_election(id: str) -> ElectionUpdateStream:
        return ElectionUpdateStream(election_id=id)

    election_id: Final[str]

    def __init__(self, election_id: str):
        super(ElectionUpdateStream, self).__init__(
            queue_name=f"election:{election_id}",
            serializer=lambda x: x.to_convention_event_string(),
        )
        self.election_id = election_id
