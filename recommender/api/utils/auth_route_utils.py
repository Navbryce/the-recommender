import os
from http.cookiejar import Cookie
from typing import Union, Dict, Optional, Callable

import jwt
from flask import Response, Request, request

from recommender.data.user.user import (
    BasicUser,
    FullUser,
    SerializableBasicUser,
    SerializableFullUser,
)
from recommender.data.user.user_manager import UserManager

AUTH_SECRET = os.environ["AUTH_SECRET"]
JWT_ENCRYPTION = "HS256"
USER_COOKIE_KEY = "user"
PROD = "prod" in os.environ


class AuthRouteUtils:
    user_manager: UserManager

    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    """
    ASSUMES USER identity has been verified
    """

    def login_as_user(self, response: Response, user: Union[SerializableBasicUser]):
        payload = {**user.__dict__, "type": user.__class__.__name__}
        jwt_payload = jwt.encode(payload, AUTH_SECRET, algorithm=JWT_ENCRYPTION)
        response.set_cookie(key=USER_COOKIE_KEY, value=jwt_payload, secure=PROD)

    def get_user_route(self, route: Callable[..., Response]) -> Callable[..., Response]:
        def wrapped(*args, **kwargs):
            return route(
                *args, **kwargs, user_maybe=self.get_user_from_session(request)
            )

        wrapped.__name__ = route.__name__
        return wrapped

    def get_user_from_session(
        self, request: Request
    ) -> Optional[SerializableBasicUser]:
        if USER_COOKIE_KEY not in request.cookies:
            return None
        payload = jwt.decode(
            request.cookies[USER_COOKIE_KEY], AUTH_SECRET, algorithms=JWT_ENCRYPTION
        )

        type = payload["type"]
        del payload["type"]
        if type == FullUser.__name__:
            return SerializableFullUser(**payload)
        else:
            return SerializableBasicUser(**payload)
