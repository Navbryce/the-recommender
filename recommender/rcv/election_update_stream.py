from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, Final, Union

from recommender.api.utils.server_sent_event import ServerSentEvent
from recommender.data.rcv.election_result import (
    CandidateRoundResult,
    DisplayableElectionResult,
    ElectionResult,
)
from recommender.data.rcv.election_status import ElectionStatus
from recommender.utilities.notification_queue import MessageStream


class ElectionUpdateEventType(Enum):
    STATUS_CHANGED = "STATUS_CHANGED"
    CANDIDATE_ADDED = "CANDIDATE_ADDED"
    RESULTS_UPDATED = "RESULTS_UPDATED"


class CandidateAddedEvent(ServerSentEvent[Dict]):
    def __init__(self, business_id: str, name: str, nominator_nickname: str):
        super(CandidateAddedEvent, self).__init__(
            id=f"{ElectionUpdateEventType.CANDIDATE_ADDED.value}-{business_id}",
            type=ElectionUpdateEventType.CANDIDATE_ADDED.value,
            data={
                "business_id": business_id,
                "name": name,
                "nominator_nickname": nominator_nickname,
            },
        )


class StatusChangedEvent(ServerSentEvent[Dict]):
    def __init__(self, status: ElectionStatus):
        super(StatusChangedEvent, self).__init__(
            id=f"{ElectionUpdateEventType.STATUS_CHANGED.value}-{status.value}",
            type=ElectionUpdateEventType.STATUS_CHANGED.value,
            data={"status": status.value},
        )


class ElectionResultEvent(ServerSentEvent[DisplayableElectionResult]):
    def __init__(self, result: DisplayableElectionResult):
        super(ElectionResultEvent, self).__init__(
            id=f"{ElectionUpdateEventType.RESULTS_UPDATED.value}-{datetime.now().timestamp()}",
            type=ElectionUpdateEventType.RESULTS_UPDATED.value,
            data=result,
        )


class ElectionUpdateStream(
    MessageStream[
        Union[ServerSentEvent[Union[ElectionStatus, None]], CandidateAddedEvent]
    ]
):
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
