from http import HTTPStatus
from typing import Union, Any, Dict, Type, Optional

from starlette.middleware.errors import (
    ServerErrorMiddleware as _ServerErrorMiddleware,
)

from .app_types import HTTPApp, ErrorHandler
from .compat import call_async
from .request import Request
from .response import Response


class HTTPError(Exception):
    """Raised when an HTTP error occurs.

    You can raise this within a view or an error handler to interrupt
    request processing.

    # Parameters
    status (int or HTTPStatus):
        the status code of the error.
    detail (any):
        extra detail information about the error. The exact rendering is
        determined by the configured error handler for `HTTPError`.

    # See Also
    - [HTTP response status codes (MDN web docs)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
    """

    def __init__(self, status: Union[int, HTTPStatus], detail: Any = ""):
        if isinstance(status, int):
            status = HTTPStatus(status)
        else:
            assert isinstance(
                status, HTTPStatus
            ), f"Expected int or HTTPStatus, got {type(status)}"
        self._status = status
        self.detail = detail

    @property
    def status_code(self) -> int:
        """Return the HTTP error's status code, e.g. `404`."""
        return self._status.value

    @property
    def status_phrase(self) -> str:
        """Return the HTTP error's status phrase, e.g. `"Not Found"`."""
        return self._status.phrase

    @property
    def title(self) -> str:
        """Return the HTTP error's title, e.g. `"404 Not Found"`."""
        return f"{self.status_code} {self.status_phrase}"

    def __str__(self):
        return self.title


class ServerErrorMiddleware(HTTPApp):
    """Return 500 response when an unhandled exception occurs.

    Adaption of Starlette's ServerErrorMiddleware.
    """

    def __init__(
        self, app: HTTPApp, handler: ErrorHandler, debug: bool = False
    ) -> None:
        self.app = app
        self.handler = handler
        self.debug = debug
        self.exception = None

    debug_response = _ServerErrorMiddleware.debug_response

    def raise_if_exception(self):
        if self.exception is not None:
            raise self.exception from None

    async def __call__(self, req: Request, res: Response):
        try:
            res = await self.app(req, res)
        except Exception as exc:
            self.exception = exc
            if self.debug:
                # In debug mode, return traceback responses.
                res = self.debug_response(req, exc)
            await call_async(self.handler, req, res, HTTPError(500))
            return res
        else:
            return res


class HTTPErrorMiddleware(HTTPApp):
    """Handler exceptions that occur while handling HTTP requests."""

    def __init__(self, app: HTTPApp, debug: bool = False) -> None:
        self.app = app
        self.debug = debug
        self._exception_handlers: Dict[Type[Exception], ErrorHandler] = {}

    def add_exception_handler(
        self, exception_class: Type[Exception], handler: ErrorHandler
    ) -> None:
        assert issubclass(exception_class, Exception)
        self._exception_handlers[exception_class] = handler

    def _lookup_exception_handler(
        self, exc: Exception
    ) -> Optional[ErrorHandler]:
        for cls, handler in self._exception_handlers.items():
            if issubclass(type(exc), cls):
                return handler
        return None

    async def __call__(self, req: Request, res: Response) -> Response:
        try:
            res = await self.app(req, res)
        except Exception as exc:
            # Try to find a handler for the exception, and handle it…
            handler = self._lookup_exception_handler(exc)
            if handler is not None:
                await call_async(handler, req, res, exc)
                return res
            # … or re-raise it.
            else:
                raise exc from None
        else:
            return res
