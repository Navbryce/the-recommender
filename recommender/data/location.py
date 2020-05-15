from collections import namedtuple
from typing import Dict

Location = namedtuple("Location", ["lat", "long"])


def from_json(json_dict: Dict) -> Location:
    return Location(**json_dict)
