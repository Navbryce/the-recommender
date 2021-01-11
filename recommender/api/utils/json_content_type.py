from typing import Callable, Dict, Optional

from flask import Response

from recommender.utilities.json_encode_utilities import json_encode


def json_content_type(
    include_status_code=False,
) -> Callable[[Callable[..., object]], Callable[..., Response]]:
    def decorator(function: Callable[..., object]) -> Callable[..., Response]:
        def wrapped_function(*args, **kwargs):
            func_output = function(*args, **kwargs)
            if include_status_code:
                data, status_code = func_output
            else:
                data = func_output
                status_code = 200

            return generate_data_json_response(data, status=status_code)

        wrapped_function.__name__ = function.__name__
        return wrapped_function

    return decorator


def generate_data_json_response(data: any, **kwargs) -> Response:
    return generate_json_response(data=data, additional_root_params=None, **kwargs)


def generate_json_response(
    data: Optional[any],
    additional_root_params: Optional[Dict] = None,
    status: int = 200,
) -> Response:
    if additional_root_params is None:
        additional_root_params = {}
    elif "data" in additional_root_params:
        raise ValueError(f'Root params cannot contain key "data"')

    if data is None:
        data = {}
    else:
        data = {"data": data}

    payload = {**data, **additional_root_params}
    payload_as_json = json_encode(payload)
    return Response(payload_as_json, mimetype="application/json", status=status)
