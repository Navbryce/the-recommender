import os

import rq_dashboard
from flask_talisman import Talisman

from recommender.env_config import PROD
from flask import Flask, Response

# We need to use an external dependency for env management because pycharm does not currently support .env files
from flask_cors import CORS

from recommender.api.utils.json_content_type import (
    json_content_type,
    generate_json_response,
)

import recommender.utilities.json_encode_utilities

from recommender.db_config import DbBase, engine


def start_api(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    CORS(app)
    Talisman(
        app,
        force_https=PROD,
        content_security_policy={
            "default-src": "'self'",
            "img-src": "*",
            "script-src": "'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src": "'self' 'unsafe-inline'",
        },
    )

    # import blue prints
    from recommender.api.auth_route import auth
    from recommender.api.business_search_route import business_search
    from recommender.api.rcv_route import rcv

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(business_search, url_prefix="/business-search")
    app.register_blueprint(rcv, url_prefix="/rcv")

    # queue metrics
    from recommender.api.global_services import auth_route_utils

    @rq_dashboard.blueprint.before_request
    def verify_auth():
        if PROD:
            auth_route_utils.require_user_before_request()

    app.config["RQ_DASHBOARD_REDIS_URL"] = os.environ["REDIS_URL"]
    app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # init tables (after everything has been imported by the services)
    DbBase.metadata.create_all(engine)

    @app.errorhandler(recommender.api.utils.http_exception.HttpException)
    def handle_http_exception(
        error: recommender.api.utils.http_exception.HttpException
    ) -> Response:
        return generate_json_response(
            data=None,
            additional_root_params={
                "message": error.message,
                "errorCode": None
                if error.error_code is None
                else error.error_code.value,
            },
            status=error.status_code,
        )

    @app.route("/wake", methods=["GET"])
    @json_content_type()
    def wake():
        # this route exists to spin up the backend server when the auth loads the site
        return None

    return app
