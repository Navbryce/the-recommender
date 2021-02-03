from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

from recommender.data.serializable import serializable_persistence_object


@serializable_persistence_object
@dataclass
class Address:
    country: str
    region: str
    city: str
    address_line: str
    zip_code: str
