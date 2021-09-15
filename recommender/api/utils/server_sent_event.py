from dataclasses import dataclass
from typing import TypeVar, Generic

from recommender.utilities.json_encode_utilities import json_encode

PAYLOAD_TYPE = TypeVar('PAYLOAD_TYPE')


@dataclass
class ServerSentEvent(Generic[PAYLOAD_TYPE]):
    id: str
    data: PAYLOAD_TYPE
    type: str

    def to_convention_event_string(self):
        return f"id: {self.id}\nevent: {self.type}\ndata: {json_encode(self.data)}\n\n"
