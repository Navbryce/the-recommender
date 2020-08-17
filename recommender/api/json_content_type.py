from typing import Callable

from flask import Response


def json_content_type(function: Callable[..., Response]) -> Callable[..., Response]:
    def wrapped_function(*args, **kwargs):
        response: Response = function(*args, **kwargs)
        response.mimetype = 'application/json'
        return response
    return wrapped_function
