#!/usr/bin/env python3
"""
The Recommender
Python >= 3.6
"""

__author__ = "Bryce"
__version__ = "0.1.0"
__license__ = "MIT"

import os

from recommender.api import start_api


def test_function():
    return 1


if __name__ == "__main__":
    start_api().run(host=os.environ["HOST"], port=os.environ["PORT"])
