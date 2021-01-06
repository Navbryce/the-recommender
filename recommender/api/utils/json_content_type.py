from typing import Callable

from flask import Response

from recommender.api.utils.json_encode_config import json_encode


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

            return generate_json_response(data, status=status_code)

        wrapped_function.__name__ = function.__name__
        return wrapped_function

    return decorator


def generate_json_response(data, status=200) -> Response:
    data_as_json = json_encode(data)
    return Response(data_as_json, mimetype="application/json", status=status)
