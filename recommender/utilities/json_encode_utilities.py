import json
from datetime import datetime
from enum import Enum
from typing import Dict, Union, List


def json_encode(data: any) -> str:
    return json.dumps(__to_serializable(data))


def __to_serializable(data: any) -> Union[List[any], Dict[str, any]]:
    if __is_directly_serializable(data):
        raise ValueError("Should only be instances of objects")

    if isinstance(data, list):
        return [__convert_value_to_serializable(value) for value in data]

    if isinstance(data, dict):
        data_dict = data
    else:
        data_dict = (
            data.__getstate__() if hasattr(data, "__getstate__") else data.__dict__
        )

    return {
        __to_camel_case(key): __convert_value_to_serializable(value)
        for key, value in data_dict.items()
    }


def __to_camel_case(value: str) -> str:
    pascal = "".join([value.title() for value in value.split("_")])
    return pascal[0].lower() + pascal[1:]


def __convert_value_to_serializable(value):
    if __is_directly_serializable(value):
        return value
    if isinstance(value, Enum):
        return value.name
    if isinstance(value, datetime):
        return str(value)
    return __to_serializable(value)


__DIRECTLY_SERIALIZABLE = [str, bool, int, float]


def __is_directly_serializable(value: any) -> bool:
    return value is None or type(value) in __DIRECTLY_SERIALIZABLE
