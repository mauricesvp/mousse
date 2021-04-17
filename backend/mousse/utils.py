"""
Mousse utility functions.

mauricesvp 2021
"""
import functools
from time import sleep
from typing import Any, Callable

import requests


def retry(times: int = 3, delay: int = 1) -> Callable[..., Any]:
    """Retry wrapper."""

    def run(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def f(*args: Any, **kwargs: Any) -> Any:
            attempts = 0
            while attempts < times:
                try:
                    return func(*args, **kwargs)
                except:  # noqa: E722
                    attempts += 1
                    sleep(delay)

        return f

    return run


@retry(5)
def html_get(url: str, timeout: int = 3) -> requests.Response:
    """Return requests.get result."""
    return requests.get(url=url, timeout=timeout)


@retry(5)
def html_post(
    url: str,
    timeout: int = 3,
    data: dict = {},
    headers: dict = {},
    cookies: dict = {},
) -> requests.Response:
    """Return requests.post result."""
    return requests.post(
        url=url, data=data, headers=headers, cookies=cookies, timeout=timeout
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
