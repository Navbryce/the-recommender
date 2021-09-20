from typing import Optional

from flask import Blueprint, Response, request, render_template

from recommender.api.global_services import user_manager, auth_route_utils
from recommender.api.utils.json_content_type import generate_data_json_response, json_content_type
from recommender.data.auth.user import BasicUser, SerializableBasicUser

auth = Blueprint("auth", __name__)


@auth.route("register", methods=["PUT"])
def register() -> Response:
    nickname = request.json["nickname"]
    user: BasicUser = user_manager.create_anonymous_user(nickname)
    serializable_user = user.to_serializable_user()
    print("TEST", nickname)

    response = generate_data_json_response(serializable_user)
    auth_route_utils.login_as_user(response, serializable_user)
    return response


@auth.route("login", methods=["GET", "POST"])
def login() -> Response:
    error = None

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = user_manager.authenticate_user(email, password)
        if user is not None:
            response = generate_data_json_response(data=user)
            auth_route_utils.login_as_user(response=response, serializable_user=user)
            return response

        error = "Incorrect username or password"

    return render_template("login.html", error=error)


@auth.route("session", methods=["GET"])
@json_content_type()
@auth_route_utils.get_user_route
def get_current_session(user_maybe: Optional[SerializableBasicUser]) -> Optional[SerializableBasicUser]:
    return user_maybe
