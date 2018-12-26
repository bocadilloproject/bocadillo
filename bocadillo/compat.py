"""Various compatibility utilities."""
import asyncio
import re
import sys
from typing import Callable, Coroutine

from starlette.concurrency import run_in_threadpool

try:
    from contextlib import asynccontextmanager
except ImportError:  # pragma: no cover
    assert sys.version_info[:2] == (3, 6)
    from async_generator import asynccontextmanager

_camel_regex = re.compile(r"(.)([A-Z][a-z]+)")
_snake_regex = re.compile(r"([a-z0-9])([A-Z])")


async def call_async(func: Callable, *args, sync=None, **kwargs) -> Coroutine:
    """Call a function in an async manner.

    # Parameters
    func (Callable):
        a callable that is either awaited (if a coroutine function)
        or run in the thread pool (if a regular function).
    sync (bool):
        A hint as to whether `func` is synchronous. If not given, it is
        inferred as `asyncio.iscoroutinefunction(func)`.

    # See Also
    - [Executing code in thread or process pools](https://docs.python.org/3/library/asyncio-eventloop.html#executing-code-in-thread-or-process-pools)
    """
    if sync is None:
        sync = not asyncio.iscoroutinefunction(func)
    if sync:
        return await run_in_threadpool(func, *args, **kwargs)
    return await func(*args, **kwargs)


def camel_to_snake(name: str) -> str:
    """Convert a `CamelCase` name to its `snake_case` version."""
    s1 = _camel_regex.sub(r"\1_\2", name)
    return _snake_regex.sub(r"\1_\2", s1).lower()
