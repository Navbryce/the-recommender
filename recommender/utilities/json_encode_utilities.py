import json
from datetime import datetime
from enum import Enum
from typing import Dict, Generic, List, TypeVar, Union


def json_encode(data: any, normalize_keys=True) -> str:
    return json.dumps(to_serializable_dict(data, normalize_keys))


KEY_TYPE = TypeVar("KEY_TYPE")
DATA_TYPE = TypeVar("DATA_TYPE")

# TODO: Switch from opt-out normalization to opt-in normalization
class NoNormalizationDict(Generic[KEY_TYPE, DATA_TYPE], Dict[KEY_TYPE, DATA_TYPE]):
    def __init__(self, *args, **kwargs):
        super(NoNormalizationDict, self).__init__(*args, **kwargs)


def to_serializable_dict(
    data: any, normalize_keys=True
) -> Union[List[any], Dict[str, any]]:
    local_normalize_keys = True

    if __is_directly_serializable(data):
        raise ValueError("Should only be instances of objects")

    if isinstance(data, list):
        return [
            __convert_value_to_serializable(value, normalize_keys) for value in data
        ]

    if isinstance(data, dict):
        if isinstance(data, NoNormalizationDict):
            local_normalize_keys = False
        data_dict = data
    else:
        data_dict = (
            data.__getstate__() if hasattr(data, "__getstate__") else data.__dict__
        )

    return {
        __to_camel_case(key)
        if normalize_keys and local_normalize_keys
        else key: __convert_value_to_serializable(value, normalize_keys)
        for key, value in data_dict.items()
    }


def __to_camel_case(value: str) -> str:
    pascal = "".join([value[0].upper() + value[1:] for value in value.split("_")])
    return pascal[0].lower() + pascal[1:]


def __convert_value_to_serializable(value, normalize_keys):
    if __is_directly_serializable(value):
        return value
    if isinstance(value, Enum):
        return value.name
    if isinstance(value, datetime):
        return str(value)
    return to_serializable_dict(value, normalize_keys)


__DIRECTLY_SERIALIZABLE = [str, bool, int, float]


def __is_directly_serializable(value: any) -> bool:
    return value is None or type(value) in __DIRECTLY_SERIALIZABLE
