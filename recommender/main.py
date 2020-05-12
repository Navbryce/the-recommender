#!/usr/bin/env python3
"""
The Recommender
Python >= 3.6
"""

__author__ = "Bryce"
__version__ = "0.1.0"
__license__ = "MIT"

import os

from dotenv import load_dotenv

from recommender.api_clients.yelp_client import YelpClient
from recommender.data.location import Location

# We need to use an external dependency for env management because pycharm does not currently support .env files
load_dotenv(verbose=True)


def main():
    """ Entry point of app """
    api_key = os.environ["YELP_API_KEY"]
    yelp_client: YelpClient = YelpClient(api_key)
    print(yelp_client.businesses_search(Location(39.244269, -76.866268)))


def test_function():
    return 1


if __name__ == "__main__":
    main()
