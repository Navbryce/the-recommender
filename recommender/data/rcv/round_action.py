from enum import Enum, unique


@unique
class RoundAction(Enum):
    ELIMINATED = "ELIMINATED"
    WON = "WON"
