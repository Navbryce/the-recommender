from enum import Enum


class ElectionStatus(Enum):
    ACTIVE = "ACTIVE"
    MARKED_COMPLETE = "MARKED_COMPLETE"
    MANUALLY_COMPLETE = "COMPLETE"
