"""Compatibility utilities (version-dependant, sync/async, etc.)."""
import asyncio
import re
import sys
from typing import Callable, Coroutine, Iterable

from starlette.concurrency import run_in_threadpool

try:
    from contextlib import asynccontextmanager
except ImportError:  # pragma: no cover
    assert sys.version_info[:2] == (3, 6)
    from async_generator import asynccontextmanager

_camel_regex = re.compile(r"(.)([A-Z][a-z]+)")
_snake_regex = re.compile(r"([a-z0-9])([A-Z])")


async def call_async(func: Callable, *args, sync=False, **kwargs) -> Coroutine:
    """Call a function in an async manner.

    If the function is synchronous (or the `sync` hint flag is set),
    it is run in the asyncio thread pool.
    """
    if sync or not asyncio.iscoroutinefunction(func):
        return await run_in_threadpool(func, *args, **kwargs)
    return await func(*args, **kwargs)


def camel_to_snake(name: str) -> str:
    """Convert a CamelCase name to its snake_case version."""
    s1 = _camel_regex.sub(r"\1_\2", name)
    return _snake_regex.sub(r"\1_\2", s1).lower()
