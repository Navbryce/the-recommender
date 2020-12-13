from time import sleep
from typing import TypeVar, Callable, Union

from requests import HTTPError, Timeout

T = TypeVar("T")


def retry_request(
    request: Callable[[], T],
    should_retry: Callable[[Union[HTTPError, Timeout]], bool],
    max_retries=5,
    delay=500,
) -> T:
    retries = 0
    while (retries <= max_retries) or max_retries == -1:
        try:
            return request()
        except (HTTPError, Timeout) as error:
            if not should_retry(error):
                raise error
            sleep(delay)
        retries += 1
