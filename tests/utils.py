import os
from contextlib import contextmanager
from typing import Any


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
