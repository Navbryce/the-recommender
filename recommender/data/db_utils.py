from sqlalchemy.exc import IntegrityError


def is_unique_key_error(error: IntegrityError):
    return "UNIQUE constraint" in str(error.orig)
