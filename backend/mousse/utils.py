"""
Mousse utility functions.

mauricesvp 2021
"""
import functools
from time import sleep
from typing import Any, Callable

import requests

from mousse.saml import gib_cookies

s = requests.Session()


def login() -> None:
    """Get and set cookies."""
    cookies = gib_cookies()
    global s
    del s
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie["name"], cookie["value"])


def retry(times: int = 3, delay: int = 1, debug: bool = False) -> Callable[..., Any]:
    """Retry wrapper."""

    def run(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def f(*args: Any, **kwargs: Any) -> Any:
            attempts = 0
            while attempts < times:
                try:
                    return func(*args, **kwargs)
                except Exception as e:  # noqa: E722
                    if debug:
                        print(func, e)
                    attempts += 1
                    sleep(delay)

        return f

    return run


@retry(times=5, debug=True)
def html_get(url: str, timeout: int = 4, bypass: bool = False) -> requests.Response:
    """Return requests.get result."""
    if bypass:
        return requests.get(url=url, timeout=timeout)

    global s
    if not s.cookies:
        login()

    return s.get(url=url, timeout=timeout)


@retry(5)
def html_post(
    url: str,
    timeout: int = 3,
    data: dict = {},
    headers: dict = {},
    # cookies: dict = {},
) -> requests.Response:
    """Return requests.post result."""
    global s
    if not s.cookies:
        login()
    return s.post(
        # url=url, data=data, headers=headers, cookies=cookies, timeout=timeout
        url=url,
        data=data,
        headers=headers,
        timeout=timeout,
    )


def array_split(array: list, batches: int) -> list:
    """Split list in equally sized portions."""
    # Credit goes to numpy.array_split
    batches = min(max(1, batches), len(array))
    batch_size, rest = divmod(len(array), batches)
    split_sizes = [0] + rest * [batch_size + 1] + (batches - rest) * [batch_size]
    for i, x in enumerate(split_sizes):
        if i == 0:
            continue
        last = split_sizes[i - 1]
        split_sizes[i] += last
    splits = []
    for i in range(batches):
        st = split_sizes[i]
        end = split_sizes[i + 1]
        splits.append(array[st:end])
    return splits
