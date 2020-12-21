from typing import Callable

from flask import Response

from recommender.api.json_encode_config import json_encode


def json_content_type(
    include_status_code=False
) -> Callable[[Callable[..., object]], Callable[..., Response]]:
    def decorator(function: Callable[..., object]) -> Callable[..., Response]:
        def wrapped_function(*args, **kwargs):
            func_output = function(*args, **kwargs)
            if include_status_code:
                data, status_code = func_output
            else:
                data = func_output
                status_code = 200
            data_as_json = json_encode(data)

            response = Response(
                data_as_json, mimetype="application/json", status=status_code
            )
            return response

        wrapped_function.__name__ = function.__name__
        return wrapped_function

    return decorator
