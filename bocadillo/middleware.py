import typing

from .app_types import ASGIApp, ErrorHandler, Receive, Scope, Send
from .compat import check_async
from .errors import HTTPError
from .request import Request
from .response import Response

if typing.TYPE_CHECKING:  # pragma: no cover
    from .applications import App


class MiddlewareMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        for callback in "before_dispatch", "after_dispatch":
            check_async(
                getattr(cls, callback),
                reason="'{name}.{callback}' must be asynchronous",
            )
        return cls


class Middleware(metaclass=MiddlewareMeta):
    """Base class for HTTP middleware classes.

    # Parameters
    inner (callable): the inner middleware that this middleware wraps.
    """

    def __init__(self, inner: ASGIApp):
        self.inner = inner

    async def before_dispatch(
        self, req: Request, res: Response
    ) -> typing.Optional[Response]:
        """Perform processing before a request is dispatched.

        If the `Response` object is returned, it will be sent and
        no further processing will be performed.
        """

    async def after_dispatch(self, req: Request, res: Response) -> None:
        """Perform processing after a request has been dispatched."""

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        assert scope["type"] == "http"

        req, res = scope["req"], scope["res"]

        before_res = await self.before_dispatch(req, res)

        if before_res is not None:
            scope["res"] = before_res
            return

        await self.inner(scope, receive, send)
        await self.after_dispatch(req, res)


class ExceptionMiddleware:
    """Handle exceptions that occur while processing requests."""

    __slots__ = ("app", "_exception_handlers")

    def __init__(
        self,
        app: ASGIApp,
        handlers: typing.Dict[typing.Type[BaseException], ErrorHandler],
    ) -> None:
        self.app = app
        self._exception_handlers = handlers

    def add_exception_handler(
        self, exception_class: typing.Type[BaseException], handler: ErrorHandler
    ) -> None:
        assert issubclass(
            exception_class, BaseException
        ), f"expected an exception class, not {type(exception_class)}"
        check_async(
            handler,
            reason=f"error handler '{handler.__name__}' must be asynchronous",
        )
        self._exception_handlers[exception_class] = handler

    def _get_exception_handler(
        self, exc: BaseException
    ) -> typing.Optional[ErrorHandler]:
        try:
            return self._exception_handlers[type(exc)]
        except KeyError:
            for cls, handler in self._exception_handlers.items():
                if isinstance(exc, cls):
                    return handler
            return None

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except BaseException as exc:  # pylint: disable=broad-except
            if scope["type"] != "http":
                raise exc from None

            req, res = scope["req"], scope["res"]

            while exc is not None:
                handler = self._get_exception_handler(exc)
                if handler is None:
                    raise exc from None
                try:
                    await handler(req, res, exc)
                except BaseException as sub_exc:  # pylint: disable=broad-except
                    exc = sub_exc
                else:
                    exc = None


class ServerErrorMiddleware:
    """Return a 500 error response when an unhandled exception occurs."""

    __slots__ = ("app", "handler")

    def __init__(self, app: ASGIApp, handler: ErrorHandler) -> None:
        self.app = app
        self.handler = handler

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except BaseException as exc:
            if scope["type"] != "http":
                raise exc from None
            req, res = scope["req"], scope["res"]
            await self.handler(req, res, HTTPError(500))
            raise exc from None


class RequestResponseMiddleware:
    """Make `req` and `res` available to HTTP routes and middleware.
    
    Note: this is mostly an implementation detail.
    """

    __slots__ = ("app",)

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def sentinel_send(message: dict):
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        req = Request(scope, receive)
        scope["req"] = req
        scope["res"] = Response(req)

        try:
            await self.app(scope, receive, sentinel_send)
        finally:
            if not response_started:
                res = scope["res"]
                refreshed_send = scope.get("send", send)
                await res(scope, receive, refreshed_send)
