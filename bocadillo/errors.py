from http import HTTPStatus
import typing

from .app_types import _E, ErrorHandler, HTTPApp
from .compat import check_async
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

    __slots__ = ("_status", "detail")

    def __init__(
        self, status: typing.Union[int, HTTPStatus], detail: typing.Any = ""
    ):
        if isinstance(status, int):
            status = HTTPStatus(  # pylint: disable=no-value-for-parameter
                status
            )
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

    Adaptation of Starlette's `ServerErrorMiddleware`.
    """

    __slots__ = ("app", "handler", "exception")

    def __init__(self, app: HTTPApp, handler: ErrorHandler) -> None:
        self.app = app
        self.handler = handler
        self.exception: typing.Optional[BaseException] = None

    def raise_if_exception(self):
        if self.exception is not None:
            raise self.exception from None

    async def __call__(self, req: Request, res: Response) -> Response:
        try:
            res = await self.app(req, res)
        except BaseException as exc:
            self.exception = exc
            await self.handler(req, res, HTTPError(500))
            return res
        else:
            return res


class HTTPErrorMiddleware(HTTPApp):
    """Handle exceptions that occur while handling HTTP requests.

    Adaptation of Starlette's `ExceptionMiddleware`.
    """

    __slots__ = ("app", "_exception_handlers")

    def __init__(self, app: HTTPApp) -> None:
        self.app = app
        self._exception_handlers: typing.Dict[
            typing.Type[BaseException], ErrorHandler
        ] = {}

    def add_exception_handler(
        self, exception_class: typing.Type[_E], handler: ErrorHandler
    ) -> None:
        assert issubclass(
            exception_class, BaseException
        ), f"expected an exception class, not {type(exception_class)}"
        check_async(
            handler,
            reason=f"error handler '{handler.__name__}' must be asynchronous",
        )
        self._exception_handlers[exception_class] = handler

    def _get_exception_handler(self, exc: _E) -> typing.Optional[ErrorHandler]:
        try:
            return self._exception_handlers[type(exc)]
        except KeyError:
            for cls, handler in self._exception_handlers.items():
                if isinstance(exc, cls):
                    return handler
            return None

    async def __call__(self, req: Request, res: Response) -> Response:
        response = self.app(req, res)

        while True:
            # Deal with errors while there's one.
            # Allows error handlers to raise exceptions to be handled
            # by other error handlers, e.g. raising an `HTTPError` in an
            # error handler.

            has_error = False

            try:
                res = (await response) or res
            except Exception as exc:  # pylint: disable=broad-except
                has_error = True
                handler = self._get_exception_handler(exc)
                if handler is None:
                    raise exc from None
                response = handler(req, res, exc)

            if not has_error:
                assert res is not None
                return res
