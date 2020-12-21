from enum import Enum
from typing import Dict, TypeVar, Type, Callable


def to_camel_case(value: str) -> str:
    pascal = "".join([value.title() for value in value.split("_")])
    return pascal[0].lower() + pascal[1:]


T = TypeVar("T")


def get_enum_state(self: Enum):
    return self.name


def serializable(cls: Type[T], get_serializable_attributes: Callable[[T], Dict] = None):
    if get_serializable_attributes is None:
        get_serializable_attributes = getattr(
            cls, "__get_public_attributes__", lambda x: x.__dict__
        )

    def new_get_state(self) -> Dict:
        return {
            to_camel_case(key): value
            for key, value in get_serializable_attributes(self).items()
        }

    cls.__getstate__ = new_get_state
    return cls
