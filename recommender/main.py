#!/usr/bin/env python3
"""
The Recommender
Python >= 3.6
"""

__author__ = "Bryce"
__version__ = "0.1.0"
__license__ = "MIT"

import logging.config
import os

import yaml
from recommender.api import start_api

if __name__ == "__main__":
    logging_config = yaml.safe_load(
        open("resources/logging-config.yaml", "r", encoding="utf-8")
    )
    logging.config.dictConfig(logging_config)

    start_api().run(host=os.environ["HOST"], port=os.environ["PORT"])
