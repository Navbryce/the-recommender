from enum import Enum
from typing import Dict, TypeVar, Type, Callable


T = TypeVar("T")


def get_enum_state(self: Enum):
    return self.name


"""
DEPRECATED
"""


def serializable(cls: Type[T], get_serializable_attributes: Callable[[T], Dict] = None):
    if get_serializable_attributes is None:
        get_serializable_attributes = getattr(
            cls, "__get_public_attributes__", lambda x: x.__dict__
        )

    cls.__getstate__ = get_serializable_attributes
    return cls
