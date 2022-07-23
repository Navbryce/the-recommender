from enum import Enum, unique


@unique
class ElectionStatus(Enum):
    IN_CREATION = "CREATION"
    VOTING = "VOTING"
    COMPLETE = "COMPLETE"
