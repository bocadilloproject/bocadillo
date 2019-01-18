import os
import time
from contextlib import contextmanager
from typing import Any
from multiprocessing import Value

import requests


@contextmanager
def function_hooks(before_value: Any = True, after_value: Any = True):
    flags = {"before": False, "after": False}

    def before(req, res, params, value=before_value):
        nonlocal flags
        assert not flags["after"]
        flags["before"] = value

    def after(req, res, params, value=after_value):
        nonlocal flags
        assert flags["before"]
        flags["after"] = value

    yield before, after

    assert flags["before"] == before_value
    assert flags["after"] == after_value


@contextmanager
def async_function_hooks(expected_before=True, expected_after=True):
    flags = {"before": False, "after": False}

    async def before(req, res, params):
        nonlocal flags
        assert not flags["after"]
        flags["before"] = True

    async def after(req, res, params):
        nonlocal flags
        assert flags["before"]
        flags["after"] = True

    yield before, after

    assert flags["before"] is expected_before
    assert flags["after"] is expected_after


@contextmanager
def class_hooks():
    flags = {"before": False, "after": False}

    class SetFlag:
        def __init__(self, flag, value):
            self.flag = flag
            self.value = value

        def __call__(self, req, res, params):
            nonlocal flags
            flags[self.flag] = self.value

    yield SetFlag("before", True), SetFlag("after", True)

    assert flags["before"]
    assert flags["after"]


@contextmanager
def env(var: str, value: str):
    initial = os.environ.get(var, None)
    os.environ[var] = value
    try:
        yield
    finally:
        os.environ.pop(var)
        if initial is not None:
            os.environ[var] = initial


class Oops(Exception):
    pass


def stops_incrementing(
    counter: Value, response: requests.Response, tolerance: int = 0
) -> bool:
    """Check that a counter stops incrementing after the response is closed.
    
    # Parameters
    counter (multiprocessing.Value):
        A counter of events.
    response (requests.Response):
        A streaming response.
    tolerance (int):
        Maximum number of events the server is allowed to send after the
        connection has been closed. Defaults to 0.
    """

    # Maximum number of events the server is allowed to send after the client
    # closed the connection.
    def wait_for_events(expect_many=False):
        nonlocal counter
        num_before = counter.value
        time.sleep(0.1)
        num_after = counter.value
        if expect_many:
            assert num_after - num_before >= 10 * tolerance
        return num_after

    sent_before_closing = wait_for_events(expect_many=True)
    response.close()
    sent_after_closing = wait_for_events() - sent_before_closing
    assert sent_after_closing <= tolerance
    return True
