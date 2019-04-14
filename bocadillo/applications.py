import os
import re
from functools import partial
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Type, Union

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
from .constants import CONTENT_TYPE
from .converters import on_validation_error
from .error_handlers import error_to_text
from .errors import HTTPError, HTTPErrorMiddleware, ServerErrorMiddleware
from .injection import _STORE
from .media import UnsupportedMediaType, get_default_handlers
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
    media_type (str):
        Determines how values given to `res.media` are serialized.
        Can be one of the supported media types.
        Defaults to `"application/json"`.
        See also [Media](../guides/http/media.md).

    # Attributes
    media_handlers (dict):
        The dictionary of media handlers.
        You can access, edit or replace this at will.
    """

    __slots__ = (
        "name",
        "asgi",
        "_prefix_to_app",
        "_name_to_prefix_and_app",
        "_static_apps",
        "media_handlers",
        "_media_type",
        "exception_middleware",
        "server_error_middleware",
        "_lifespan",
        "_store",
        "_frozen",
    )

    def __init__(
        self, name: str = None, *, media_type: str = CONTENT_TYPE.JSON
    ):
        super().__init__()

        self.name = name

        # Base ASGI app
        self.asgi = self.dispatch

        # Mounted (children) apps.
        self._prefix_to_app: Dict[str, Any] = {}
        self._name_to_prefix_and_app: Dict[str, Tuple[str, App]] = {}
        self._static_apps: Dict[str, WhiteNoise] = {}

        # Media
        self.media_handlers = get_default_handlers()
        self._media_type = ""
        self.media_type = media_type

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

    @property
    def media_type(self) -> str:
        """The media type configured when instanciating the application."""
        return self._media_type

    @media_type.setter
    def media_type(self, media_type: str):
        if media_type not in self.media_handlers:
            raise UnsupportedMediaType(media_type, handlers=self.media_handlers)
        self._media_type = media_type

    def url_for(self, name: str, **kwargs) -> str:
        # Implement route name lookup accross sub-apps.
        try:
            return super().url_for(name, **kwargs)
        except HTTPError as exc:
            app_name, _, name = name.partition(":")

            if not name:
                # No app name given.
                raise exc from None

            return self._url_for_app(app_name, name, **kwargs)

    def _url_for_app(self, app_name: str, name: str, **kwargs) -> str:
        if app_name == self.name:
            # NOTE: this allows to reference this app's routes in
            # both with or without the namespace.
            return self._get_own_url_for(name, **kwargs)

        try:
            prefix, app = self._name_to_prefix_and_app[app_name]
        except KeyError as key_exc:
            raise HTTPError(404) from key_exc
        else:
            return prefix + app.url_for(name, **kwargs)

    def _get_own_url_for(self, name: str, **kwargs) -> str:
        # NOTE: recipes hook into this method to prepend their
        # prefix to the URL.
        return super().url_for(name, **kwargs)

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

        self._prefix_to_app[prefix] = app

        if isinstance(app, App) and app.name is not None:
            self._name_to_prefix_and_app[app.name] = (prefix, app)

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
        res = Response(
            req,
            media_type=self.media_type,
            media_handler=self.media_handlers[self.media_type],
        )

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
            for prefix, app in self._prefix_to_app.items():
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
