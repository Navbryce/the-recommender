from enum import Enum, unique


@unique
class RoundAction(Enum):
    ELIMINATED = "ELIMINATED"
    WON = "WON"
    WON_VIA_TIEBREAKER = "WON_BY_TIEBREAKER"
