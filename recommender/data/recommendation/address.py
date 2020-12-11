from dataclasses import dataclass

from recommender.data.serializable import Serializable


@dataclass
class Address(Serializable):
    country: str
    region: str
    city: str
    address_line: str
    zip_code: str
