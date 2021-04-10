"""
mousse.utils

mauricesvp 2021
"""
import functools
from time import sleep
from typing import no_type_check

import requests

from mousse.log import setup_logger

logger = setup_logger("mousse_utils")


@no_type_check
def retry(times: int = 3, delay: int = 1):
    def run(func):
        @functools.wraps(func)
        def f(*args, **kwargs):
            attempts = 0
            while attempts < times:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.debug(f"Trying again. {func} .{e}")
                    attempts += 1
                    sleep(delay)

        return f

    return run


@retry(5)
def html_get(url: str, timeout: int = 5) -> requests.Response:
    return requests.get(url=url, timeout=timeout)


@retry(5)
def html_post(
    url: str,
    timeout: int = 5,
    data: dict = None,
    headers: dict = None,
    cookies: dict = None,
) -> requests.Response:
    return requests.post(
        url=url, data=data, headers=headers, cookies=cookies, timeout=timeout
    )
