from enum import Enum
from typing import Callable, Dict, Type, TypeVar

T = TypeVar("T")


def get_enum_state(self: Enum):
    return self.name


"""
DEPRECATED
"""


def serializable_persistence_object(
    cls: Type[T], get_serializable_attributes: Callable[[T], Dict] = None
):
    def __getstate__(self) -> Dict:
        return {key: value for key, value in self.__dict__.items() if key[0] != "_"}

    cls.__getstate__ = __getstate__

    return cls
