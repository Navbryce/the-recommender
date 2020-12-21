from dataclasses import dataclass
from enum import Enum
from typing import Optional

from recommender.data.serializable import serializable


class ErrorCode(Enum):
    NO_BUSINESSES_FOUND = "NO_BUSINESSES_FOUND"


@serializable
@dataclass
class HttpException(Exception):
    message: str
    error_code: ErrorCode
    status_code: int

    def __init__(self, message: str, status_code: int, error_code: Optional[ErrorCode]):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)
