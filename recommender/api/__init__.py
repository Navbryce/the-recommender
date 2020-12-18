from dotenv import load_dotenv
from flask import Flask

# We need to use an external dependency for env management because pycharm does not currently support .env files
from flask_cors import CORS

from recommender.api.json_content_type import json_content_type

load_dotenv(verbose=True)

import recommender.api.json_encode_config

from recommender.db_config import DbBase, engine


def start_api(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    # import blue prints
    from recommender.api.business_search_route import business_search

    app.register_blueprint(business_search, url_prefix="/business-search")

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # init tables (after everything has been imported by the services)
    DbBase.metadata.create_all(engine)

    @app.route("/wake", methods=["GET"])
    @json_content_type
    def wake():
        # this route exists to spin up the backend server when the user loads the site
        return None

    return app
