from dataclasses import dataclass


@dataclass
class Address:
    country: str
    region: str
    city: str
    address_line: str
    zip_code: str
