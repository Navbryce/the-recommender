from enum import Enum, unique


@unique
class ElectionStatus(Enum):
    IN_CREATION = "CREATION"
    VOTING = "VOTING"
    MARKED_COMPLETE = "MARKED_COMPLETE"
    MANUALLY_COMPLETE = "COMPLETE"
