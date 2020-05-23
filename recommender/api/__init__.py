import os

from flask import Flask

from dotenv import load_dotenv

# We need to use an external dependency for env management because pycharm does not currently support .env files
load_dotenv(verbose=True)


def start_api(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # register blue prints
    from recommender.api.business_search import business_search

    app.register_blueprint(business_search, url_prefix="/business-search")

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    return app
