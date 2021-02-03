from dataclasses import dataclass
from enum import Enum
from typing import Optional

from recommender.data.serializable import serializable_persistence_object


class ErrorCode(Enum):
    INVALID_ELECTION_STATUS = "INVALID_ELECTION_STATUS", 409
    NO_BUSINESSES_FOUND = "NO_BUSINESSES_FOUND", 404
    NO_ELECTION_FOUND = "NO_ELECTION_FOUND", 404

    @property
    def status_code(self) -> int:
        return self.value[1]

    @property
    def code_value(self) -> str:
        return self.value[0]


@serializable_persistence_object
@dataclass
class HttpException(Exception):
    message: str
    error_code: Optional[str] = None
    status_code: Optional[int] = None

    def __init__(
            self, message: str, status_code: Optional[int] = None, error_code: Optional[ErrorCode] = None
    ):
        if error_code is not None and status_code is not None:
            raise ValueError("Provided both an error code and a status code")
        if error_code is None and status_code is None:
            raise ValueError("No error code or status code provided")
        if error_code:
            status_code = error_code.status_code
        self.message = message
        self.status_code = status_code
        self.error_code = error_code.code_value
        super().__init__(message)
