from dataclasses import dataclass


@dataclass
class Recommendation:
    session_id: str
    business_id: str
    distance: float

    def __init(self, session_id, business_id, distance):
        super().__init__(
            session_id=session_id, business_id=business_id, distance=distance
        )
