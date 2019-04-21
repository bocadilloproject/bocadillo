import typing

from starlette.middleware.wsgi import WSGIResponder
from starlette.routing import Lifespan

from .app_types import (
    _E,
    ASGIApp,
    ASGIAppInstance,
    ErrorHandler,
    EventHandler,
    Receive,
    Scope,
    Send,
)
from .config import settings
from .compat import WSGIApp
from .error_handlers import error_to_text, error_to_json
from .errors import HTTPError, HTTPErrorMiddleware, ServerErrorMiddleware
from .injection import STORE
from .meta import DocsMeta
from .middleware import ASGIMiddleware
from .request import Request
from .response import Response
from .routing import RoutingMixin

if typing.TYPE_CHECKING:  # pragma: no cover
    from .recipes import Recipe


class App(RoutingMixin, metaclass=DocsMeta):
    """The all-mighty application class.

    This class implements the [ASGI](https://asgi.readthedocs.io) protocol.

    # Example

    ```python
    >>> from bocadillo import App
    >>> app = App()
    ```

    # Parameters
    name (str):
        An optional name for the app.
    """

    __slots__ = (
        "name",
        "asgi",
        "exception_middleware",
        "server_error_middleware",
        "_children",
        "_lifespan",
    )

    def __init__(self, name: str = None):
        super().__init__()

        self.name = name

        # Base ASGI app
        self.asgi = self.dispatch

        # Mounted (children) apps.
        self._children: typing.Dict[str, typing.Any] = {}

        # HTTP middleware
        self.exception_middleware = HTTPErrorMiddleware(self.http_router)
        self.server_error_middleware = ServerErrorMiddleware(
            self.exception_middleware, handler=error_to_text
        )
        self.add_error_handler(HTTPError, error_to_json)

        # Lifespan middleware
        self._lifespan = Lifespan()

        # Startup checks.
        @self.on("startup")
        async def check_app():
            if not settings.configured:
                raise RuntimeError(
                    "You must call `configure(app)` before serving `app`. "
                )

        # NOTE: discover providers from `providerconf` at instanciation time,
        # so that further declared views correctly resolve providers.
        STORE.discover_default()

    def mount(self, prefix: str, app: typing.Union["App", ASGIApp, WSGIApp]):
        """Mount another WSGI or ASGI app at the given prefix.

        [WSGI]: https://wsgi.readthedocs.io
        [ASGI]: https://asgi.readthedocs.io

        # Parameters
        prefix (str):
            A path prefix where the app should be mounted, e.g. `"/myapp"`.
        app:
            an object implementing the [WSGI] or [ASGI] protocol.
        """
        if not prefix.startswith("/"):
            prefix = "/" + prefix

        self._children[prefix] = app

    def recipe(self, recipe: "Recipe"):
        """Apply a recipe.

        # Parameters
        recipe:
            a #::bocadillo.recipes#Recipe or #::bocadillo.recipes#RecipeBook
            to be applied to the application.

        # See Also
        - [Recipes](../guides/architecture/recipes.md)
        """
        recipe.apply(self)

    def add_error_handler(
        self, exception_cls: typing.Type[_E], handler: ErrorHandler
    ):
        """Register a new error handler.

        # Parameters
        exception_cls (exception class):
            The type of exception that should be handled.
        handler (callable):
            The actual error handler, which is called when an instance of
            `exception_cls` is caught.
            Should accept a request, response and exception parameters.
        """
        self.exception_middleware.add_exception_handler(exception_cls, handler)

    def error_handler(self, exception_cls: typing.Type[Exception]):
        """Register a new error handler (decorator syntax).

        # See Also
        - [add_error_handler](#add-error-handler)
        """

        def wrapper(handler):
            self.add_error_handler(exception_cls, handler)
            return handler

        return wrapper

    def add_middleware(self, middleware_cls, **kwargs):
        """Register a middleware class.

        # Parameters
        middleware_cls: a subclass of #::bocadillo.middleware#Middleware.

        # See Also
        - [Middleware](../guides/http/middleware.md)
        """
        self.exception_middleware.app = middleware_cls(
            self.exception_middleware.app, app=self, **kwargs
        )

    def add_asgi_middleware(self, middleware_cls, **kwargs):
        """Register an ASGI middleware class.

        # Parameters
        middleware_cls: a class that complies with the ASGI specification.

        # See Also
        - [ASGI middleware](../guides/agnostic/asgi-middleware.md)
        - [ASGI](https://asgi.readthedocs.io)
        """
        args = (self,) if issubclass(middleware_cls, ASGIMiddleware) else ()
        self.asgi = middleware_cls(self.asgi, *args, **kwargs)

    def on(self, event: str, handler: typing.Optional[EventHandler] = None):
        """Register an event handler.

        # Parameters
        event (str):
            Either `"startup"` (when the server boots) or `"shutdown"`
            (when the server stops).
        handler (callback, optional):
            The event handler. If not given, this should be used as a
            decorator.

        # Example

        ```python
        @app.on("startup")
        async def startup():
            pass

        async def shutdown():
            pass

        app.on("shutdown", shutdown)
        ```
        """
        if handler is None:

            def register(func):
                self._lifespan.add_event_handler(event, func)
                return func

            return register

        self._lifespan.add_event_handler(event, handler)
        return handler

    def dispatch_http(self, scope: Scope) -> ASGIAppInstance:
        async def asgi(receive: Receive, send: Send):
            req = Request(scope, receive)
            res = Response(req)

            res: Response = await self.server_error_middleware(req, res)
            await res(receive, send)
            # Re-raise the exception to allow the server to log the error
            # and for the test client to optionally re-raise it too.
            self.server_error_middleware.raise_if_exception()

        return asgi

    def dispatch_websocket(self, scope: Scope) -> ASGIAppInstance:
        async def asgi(receive: Receive, send: Send):
            await self.websocket_router(scope, receive, send)

        return asgi

    def dispatch(self, scope: Scope) -> ASGIAppInstance:
        path: str = scope["path"]

        # Return a sub-mounted extra app, if found
        for prefix, app in self._children.items():
            if not path.startswith(prefix):
                continue
            # Remove prefix from path so that the request is made according
            # to the mounted app's point of view.
            scope["path"] = path[len(prefix) :]
            try:
                return app(scope)
            except TypeError:
                return WSGIResponder(app, scope)

        if scope["type"] == "websocket":
            return self.dispatch_websocket(scope)

        assert scope["type"] == "http"
        return self.dispatch_http(scope)

    def __call__(self, scope: Scope) -> ASGIAppInstance:
        if scope["type"] == "lifespan":
            return self._lifespan(scope)
        return self.asgi(scope)
