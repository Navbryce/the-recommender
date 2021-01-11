from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


@dataclass
class DisplayableCategory:
    id: str
    label: str
