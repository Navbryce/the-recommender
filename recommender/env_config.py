import os

from dotenv import load_dotenv

load_dotenv(verbose=True)

PROD = os.environ["IS_PROD"].lower() == "true"
