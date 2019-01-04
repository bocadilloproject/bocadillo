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

    def __init__(self, app: HTTPApp, debug: bool = False) -> None:
        self.app = app
        self.handler = error_to_text
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
        self._exception_handlers: Dict[Type[Exception], ErrorHandler] = {
            HTTPError: error_to_text
        }

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


# Built-in HTTP error handlers.


async def error_to_html(req: Request, res: Response, exc: HTTPError):
    """Convert an exception to an HTML response.

    The response contains a `<h1>` tag with the error's `title` and,
    if provided, a `<p>` tag with the error's `detail`.

    # Example

    ```html
    <h1>403 Forbidden</h1>
    <p>You do not have the permissions to perform this operation.</p>
    ```
    """
    res.status_code = exc.status_code
    html = f"<h1>{exc.title}</h1>"
    if exc.detail:
        html += f"\n<p>{exc.detail}</p>"
    res.html = html


async def error_to_media(req: Request, res: Response, exc: HTTPError):
    """Convert an exception to a media response.

    The response contains the following items:

    - `error`: the error's `title`
    - `status`: the error's `status_code`
    - `detail`: the error's `detail` (if provided)

    # Example

    ```json
    {
        "error": "403 Forbidden",
        "status": 403,
        "detail": "You do not have the permissions to perform this operation."
    }
    ```
    """
    res.status_code = exc.status_code
    media = {"error": exc.title, "status": exc.status_code}
    if exc.detail:
        media["detail"] = exc.detail
    res.media = media


async def error_to_text(req: Request, res: Response, exc: HTTPError):
    """Convert an exception to a plain text response.

    The response contains a line with the error's `title` and, if provided,
    a line for the error's `detail`.

    # Example
    ```
    403 Forbidden
    You do not have the permissions to perform this operation.
    ```
    """
    res.status_code = exc.status_code
    text = exc.title
    if exc.detail:
        text += f"\n{exc.detail}"
    res.text = text
