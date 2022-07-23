import os

from dotenv import load_dotenv


def parse_env_flag(key: str) -> bool:
    if key not in os.environ:
        return False
    return os.environ[key].lower() == "ture"


load_dotenv(verbose=True)
HEROKU = parse_env_flag("IS_HEROKU")
PROD = parse_env_flag("IS_PROD")

