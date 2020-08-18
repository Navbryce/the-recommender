from typing import Callable

import jsonpickle
from flask import Response


def json_content_type(function: Callable[..., object]) -> Callable[..., Response]:
    def wrapped_function(*args, **kwargs):
        data_to_encode = function(*args, **kwargs)

        data_as_json = jsonpickle.encode(
            data_to_encode,
            unpicklable=False
        )

        response = Response(data_as_json)
        response.mimetype = 'application/json'
        return response
    return wrapped_function
