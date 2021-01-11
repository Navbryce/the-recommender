from flask import Blueprint, Response, request, render_template, redirect

from recommender.api.global_services import user_manager, auth_route_utils
from recommender.api.utils.json_content_type import generate_data_json_response

auth = Blueprint("auth", __name__)


@auth.route("register", methods=["PUT"])
def register() -> Response:
    nickname = request.form["nickname"]
    return auth_route_utils.generate_user_created_response_and_login(
        user_manager.create_anonymous_user(nickname).to_serializable_user()
    )


@auth.route("login", methods=["GET", "POST"])
def login() -> Response:
    error = None

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = user_manager.get_user(email, password)
        if user is not None:
            response = generate_data_json_response(data=user)
            auth_route_utils.login_as_user(response=response, user=user)
            return response

        error = "Incorrect username or password"

    return render_template("login.html", error=error)
