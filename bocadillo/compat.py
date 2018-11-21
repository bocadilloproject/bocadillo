import inspect
from typing import Callable, Coroutine

from starlette.concurrency import run_in_threadpool

from .types import WSGIApp


def empty_wsgi_app() -> WSGIApp:
    """Return a WSGI app that always returns 404 Not Found."""

    def wsgi(environ, start_response):
        status = '404 Not Found'
        body = b'Not Found'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [body]

    return wsgi


async def call_async(func: Callable, *args, sync=False, **kwargs) -> Coroutine:
    """Call a function in an async manner.

    If the function is synchronous (or the `sync` hint flag is set),
    it is run in the asyncio thread pool.
    """
    if sync or not inspect.iscoroutinefunction(func):
        return await run_in_threadpool(func, *args, **kwargs)
    return await func(*args, **kwargs)
