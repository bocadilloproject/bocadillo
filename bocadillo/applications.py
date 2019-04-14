import os
import re
from functools import partial
from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Union

from starlette.middleware.wsgi import WSGIResponder
from starlette.routing import Lifespan
import typesystem

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
from .compat import WSGIApp, nullcontext
from .converters import on_validation_error
from .error_handlers import error_to_text
from .errors import HTTPError, HTTPErrorMiddleware, ServerErrorMiddleware
from .injection import _STORE
from .meta import DocsMeta
from .middleware import ASGIMiddleware
from .request import Request
from .response import Response
from .routing import RoutingMixin
from .staticfiles import WhiteNoise

if TYPE_CHECKING:  # pragma: no cover
    from .recipes import Recipe


_SCRIPT_REGEX = re.compile(r"(.*)\.py")


def _get_module(script_path: str) -> Optional[str]:  # pragma: no cover
    match = _SCRIPT_REGEX.match(script_path)
    if match is None:
        return None
    return match.group(1).replace(os.path.sep, ".")


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
        "_children",
        "_static_apps",
        "exception_middleware",
        "server_error_middleware",
        "_lifespan",
        "_store",
        "_frozen",
    )

    def __init__(self, name: str = None):
        super().__init__()

        self.name = name

        # Base ASGI app
        self.asgi = self.dispatch

        # Mounted (children) apps.
        self._children: Dict[str, Any] = {}
        self._static_apps: Dict[str, WhiteNoise] = {}

        # HTTP middleware
        self.exception_middleware = HTTPErrorMiddleware(self.http_router)
        self.server_error_middleware = ServerErrorMiddleware(
            self.exception_middleware, handler=error_to_text
        )
        self.add_error_handler(HTTPError, error_to_text)
        self.add_error_handler(typesystem.ValidationError, on_validation_error)

        # Lifespan middleware
        self._lifespan = Lifespan()

        # Startup checks.
        @self.on("startup")
        async def check_app():
            if not settings.configured:
                raise RuntimeError(
                    "You must call `configure(app)` before serving `app`. "
                )

        # Providers.

        self._store = _STORE
        self._frozen = False

        # NOTE: discover providers from `providerconf` at instanciation time,
        # so that further declared views correctly resolve providers.
        self._store.discover_default()

        self.on("startup", self._store.enter_session)
        self.on("shutdown", self._store.exit_session)

    def _app_providers(self):
        if not self._frozen:
            self._store.freeze()
            self._frozen = True
        return nullcontext()

    def mount(self, prefix: str, app: Union["App", ASGIApp, WSGIApp]):
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

        if isinstance(app, WhiteNoise):
            self._static_apps[prefix] = app

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

    def add_error_handler(self, exception_cls: Type[_E], handler: ErrorHandler):
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

    def error_handler(self, exception_cls: Type[Exception]):
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

    def on(self, event: str, handler: Optional[EventHandler] = None):
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

    async def dispatch_http(self, receive: Receive, send: Send, scope: Scope):
        req = Request(scope, receive)
        res = Response(req)

        res: Response = await self.server_error_middleware(req, res)
        await res(receive, send)
        # Re-raise the exception to allow the server to log the error
        # and for the test client to optionally re-raise it too.
        self.server_error_middleware.raise_if_exception()

    async def dispatch_websocket(
        self, receive: Receive, send: Send, scope: Scope
    ):
        await self.websocket_router(scope, receive, send)

    def dispatch(self, scope: Scope) -> ASGIAppInstance:
        with self._app_providers():
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
                return partial(self.dispatch_websocket, scope=scope)

            assert scope["type"] == "http"
            return partial(self.dispatch_http, scope=scope)

    def __call__(self, scope: Scope) -> ASGIAppInstance:
        if scope["type"] == "lifespan":
            return self._lifespan(scope)
        return self.asgi(scope)
