from dataclasses import dataclass

from recommender.data.serializable import serializable


@serializable
@dataclass
class Address:
    country: str
    region: str
    city: str
    address_line: str
    zip_code: str
