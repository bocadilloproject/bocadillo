import inspect
import typing

try:
    # >= 3.7
    from contextlib import nullcontext  # pylint: disable=unused-import
except ImportError:  # pragma: no cover
    from contextlib import contextmanager

    @contextmanager
    def nullcontext(enter_result: typing.Any = None):
        yield enter_result


_V = typing.TypeVar("_V")


class ExpectedAsync(Exception):
    """Raised when a feature expected an asynchronous function."""


def check_async(func, reason: str):
    if not inspect.iscoroutinefunction(func):
        message = f"{reason}. Hint: use `async def` instead of `def`."
        raise ExpectedAsync(message)


def is_asgi3(app: typing.Callable) -> bool:
    sig = inspect.signature(app.__call__)
    return "receive" in sig.parameters or "send" in sig.parameters


# For 3.6 compatibility (only available in 3.7+).
class asyncnullcontext:
    def __init__(self, enter_result: typing.Any = None):
        self._result = enter_result

    async def __aenter__(self):
        return self._result

    async def __aexit__(self, *args):
        pass


# WSGI

Environ = dict
StartResponse = typing.Callable[[str, typing.List[str]], None]
WSGIApp = typing.Callable[[Environ, StartResponse], typing.List[bytes]]


def empty_wsgi_app() -> WSGIApp:
    """Return a WSGI app that always returns `404 Not Found`."""

    def wsgi(environ, start_response):
        status = "404 Not Found"
        body = b"Not Found"
        headers = [("Content-Type", "text/plain")]
        start_response(status, headers)
        return [body]

    return wsgi
