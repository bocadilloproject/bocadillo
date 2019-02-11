import traceback
from http import HTTPStatus
from typing import Any, Dict, Optional, Type, Union

import jinja2
from starlette.responses import HTMLResponse, PlainTextResponse

from .app_types import ErrorHandler, HTTPApp
from .compat import call_async
from .misc import read_asset
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

    Adaptation of Starlette's ServerErrorMiddleware.
    """

    _template_name = "server_error.jinja"

    def __init__(
        self, app: HTTPApp, handler: ErrorHandler, debug: bool = False
    ) -> None:
        self.app = app
        self.handler = handler
        self.debug = debug
        self.exception: Optional[BaseException] = None
        self.jinja = jinja2.Environment()

    def generate_html(self, req: Request, exc: BaseException) -> str:
        template = self.jinja.from_string(read_asset(self._template_name))
        tb_exc = traceback.TracebackException.from_exception(
            exc, capture_locals=True
        )
        return template.render(
            exc_type=exc.__class__.__name__,
            exc=exc,
            url_path=req.url.path,
            frames=tb_exc.stack,
        )

    def generate_plain_text(self, exc: BaseException) -> str:
        return "".join(traceback.format_tb(exc.__traceback__))

    def debug_response(self, req: Request, exc: BaseException) -> Response:
        accept = req.headers.get("accept", "")

        if "text/html" in accept:
            content = self.generate_html(req, exc)
            return HTMLResponse(content, status_code=500)

        content = self.generate_plain_text(exc)
        return PlainTextResponse(content, status_code=500)

    def raise_if_exception(self):
        if self.exception is not None:
            raise self.exception from None

    async def __call__(self, req: Request, res: Response):
        try:
            res = await self.app(req, res)
        except BaseException as exc:
            self.exception = exc
            if self.debug:
                # In debug mode, return traceback responses.
                res = self.debug_response(req, exc)
            await call_async(self.handler, req, res, HTTPError(500))
            return res
        else:
            return res


class HTTPErrorMiddleware(HTTPApp):
    """Handle exceptions that occur while handling HTTP requests.

    Adaptation of Starlette's ExceptionMiddleware.
    """

    def __init__(self, app: HTTPApp, debug: bool = False) -> None:
        self.app = app
        self.debug = debug
        self._exception_handlers: Dict[Type[BaseException], ErrorHandler] = {}

    def add_exception_handler(
        self, exception_class: Type[BaseException], handler: ErrorHandler
    ) -> None:
        assert issubclass(exception_class, BaseException)
        self._exception_handlers[exception_class] = handler

    def _get_exception_handler(
        self, exc: BaseException
    ) -> Optional[ErrorHandler]:
        for cls, handler in self._exception_handlers.items():
            if issubclass(type(exc), cls):
                return handler
        return None

    async def __call__(self, req: Request, res: Response) -> Response:
        try:
            res = await self.app(req, res)
        except BaseException as exc:
            handler = self._get_exception_handler(exc)
            if handler is None:
                raise exc from None
            await call_async(handler, req, res, exc)
            return res
        else:
            return res
