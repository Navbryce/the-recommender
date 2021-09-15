import os
from typing import Optional, Callable

import jwt
from flask import Response, Request, request, g

from recommender.api.utils.http_exception import HttpException
from recommender.api.utils.json_content_type import (
    generate_json_response,
    generate_data_json_response,
)
from recommender.data.auth.user import SerializableBasicUser, SerializableFullUser
from recommender.auth.user_manager import UserManager
from recommender.env_config import PROD
from recommender.utilities.json_encode_utilities import to_serializable_dict

AUTH_SECRET = os.environ["AUTH_SECRET"]
JWT_ENCRYPTION = "HS256"
USER_COOKIE_KEY = "auth"


class AuthRouteUtils:
    user_manager: UserManager

    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    def get_user_route(self, route: Callable[..., Response]) -> Callable[..., Response]:
        def wrapped(*args, **kwargs):
            return route(
                *args, **kwargs, user_maybe=self.get_user_from_session(request)
            )

        wrapped.__name__ = route.__name__
        return wrapped

    def require_user_route(
            self
    ) -> Callable[[Callable[..., Response]], Callable[..., Response]]:
        def decorator(route: Callable[..., Response]) -> Callable[..., Response]:
            def wrapped(*args, **kwargs):
                user = self.get_user_from_session(request)
                if user is None:
                    raise AuthorizationException()
                return route(*args, **kwargs, user=user)

            wrapped.__name__ = route.__name__
            return wrapped

        return decorator

    """
    Adds the serializable auth to g.auth.
    An alternative to require_user_route (which passes the auth direclty as a param)
    """

    def require_user_before_request(self):
        user = self.get_user_from_session(request)
        if user is None:
            raise AuthorizationException()
        g.user = user


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

        if type == SerializableFullUser.__name__:
            return SerializableFullUser(**payload)
        else:
            return SerializableBasicUser(**payload)

    """
    ASSUMES USER identity has been verified
    """

    def login_as_user(self, response: Response, serializable_user: SerializableBasicUser):
        jwt_payload = jwt.encode(to_serializable_dict(serializable_user, normalize_keys=False), AUTH_SECRET, algorithm=JWT_ENCRYPTION)
        response.set_cookie(
            key=USER_COOKIE_KEY, value=jwt_payload, secure=PROD, httponly=True
        )


class AuthorizationException(HttpException):
    def __init__(self):
        super(AuthorizationException, self).__init__(
            message="User not logged in", status_code=401
        )
