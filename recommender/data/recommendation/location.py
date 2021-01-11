from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class Location:
    lat: float
    long: float

    @staticmethod
    def from_json_dict(json_dict: Dict) -> Location:
        return Location(**json_dict)

    def __composite_values__(self):
        return self.lat, self.long
