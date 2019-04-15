import time
from contextlib import contextmanager
from multiprocessing import Value
import typing

import requests


@contextmanager
def function_hooks(
    expected_before: typing.Any = True, expected_after: typing.Any = True
):
    flags = {"before": False, "after": False}

    async def before(req, res, params, value=expected_before):
        nonlocal flags
        assert not flags["after"]
        flags["before"] = value

    async def after(req, res, params, value=expected_after):
        nonlocal flags
        assert flags["before"]
        flags["after"] = value

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

        async def __call__(self, req, res, params):
            nonlocal flags
            flags[self.flag] = self.value

    yield SetFlag("before", True), SetFlag("after", True)

    assert flags["before"]
    assert flags["after"]


def stops_incrementing(
    counter: Value, response: requests.Response, tolerance: int = 15
) -> bool:
    # Check that a counter stops incrementing after the response is closed.

    # tolerance (int):
    # Maximum number of events the server is allowed to send after the
    # connection has been closed.

    def wait_for_events(expect_many=False):
        nonlocal counter
        num_before = counter.value
        time.sleep(0.1)
        num_after = counter.value
        if expect_many:
            assert num_after - num_before >= 5 * tolerance, (
                num_after,
                num_before,
                tolerance,
            )
        return num_after

    sent_before_closing = wait_for_events(expect_many=True)
    response.close()
    sent_after_closing = wait_for_events() - sent_before_closing
    assert sent_after_closing <= tolerance, (sent_after_closing, tolerance)
    return True
