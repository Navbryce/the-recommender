from dataclasses import dataclass


@dataclass
class Recommendation:
    id: str
    business_id: str
    distance: float
