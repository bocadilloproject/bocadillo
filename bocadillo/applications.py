import os
from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.wsgi import WSGIResponder
from starlette.routing import Lifespan
from starlette.testclient import TestClient
from uvicorn.config import get_logger
from uvicorn.main import run
from uvicorn.reloaders.statreload import StatReload

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
from .compat import WSGIApp
from .constants import CONTENT_TYPE, DEFAULT_CORS_CONFIG
from .deprecation import deprecated
from .error_handlers import error_to_text
from .errors import HTTPError, HTTPErrorMiddleware, ServerErrorMiddleware
from .media import UnsupportedMediaType, get_default_handlers
from .meta import DocsMeta
from .request import Request
from .response import Response
from .routing import RoutingMixin
from .staticfiles import static
from .templates import TemplatesMixin

if TYPE_CHECKING:
    from .recipes import Recipe


class App(TemplatesMixin, RoutingMixin, metaclass=DocsMeta):
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
    static_dir (str):
        The name of the directory containing static files, relative to
        the application entry point. Set to `None` to not serve any static
        files.
        Defaults to `"static"`.
    static_root (str):
        The path prefix for static assets.
        Defaults to `"static"`.
    allowed_hosts (list of str, optional):
        A list of hosts which the server is allowed to run at.
        If the list contains `"*"`, any host is allowed.
        Defaults to `["*"]`.
    enable_cors (bool):
        If `True`, Cross Origin Resource Sharing will be configured according
        to `cors_config`. Defaults to `False`.
        See also [CORS](../guides/http/middleware.md#cors).
    cors_config (dict):
        A dictionary of CORS configuration parameters.
        Defaults to `dict(allow_origins=[], allow_methods=["GET"])`.
    enable_hsts (bool):
        If `True`, enable HSTS (HTTP Strict Transport Security) and automatically
        redirect HTTP traffic to HTTPS.
        Defaults to `False`.
        See also [HSTS](../guides/http/middleware.md#hsts).
    enable_gzip (bool):
        If `True`, enable GZip compression and automatically
        compress responses for clients that support it.
        Defaults to `False`.
        See also [GZip](../guides/http/middleware.md#gzip).
    gzip_min_size (int):
        If specified, compress only responses that
        have more bytes than the specified value.
        Defaults to `1024`.
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

    def __init__(
        self,
        name: str = None,
        *,
        static_dir: Optional[str] = "static",
        static_root: Optional[str] = "static",
        allowed_hosts: List[str] = None,
        enable_cors: bool = False,
        cors_config: dict = None,
        enable_hsts: bool = False,
        enable_gzip: bool = False,
        gzip_min_size: int = 1024,
        media_type: str = CONTENT_TYPE.JSON,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.name = name

        # Debug mode defaults to `False` but it can be set in `.run()`.
        self._debug = False

        # Base ASGI app
        self.asgi = self.dispatch

        # Mounted apps
        self._prefix_to_app: Dict[str, Any] = {}
        self._name_to_prefix_and_app: Dict[str, Tuple[str, App]] = {}

        # Test client
        self.client = self.build_client()

        # Static files
        if static_dir is not None:
            if static_root is None:
                static_root = static_dir
            self.mount(static_root, static(static_dir))

        # Media
        self.media_handlers = get_default_handlers()
        self._media_type = ""
        self.media_type = media_type

        # HTTP middleware
        self.exception_middleware = HTTPErrorMiddleware(
            self.http_router, debug=self._debug
        )
        self.server_error_middleware = ServerErrorMiddleware(
            self.exception_middleware, handler=error_to_text, debug=self._debug
        )
        self.add_error_handler(HTTPError, error_to_text)

        # Lifespan middleware
        self._lifespan = Lifespan()

        # ASGI middleware
        if allowed_hosts is None:
            allowed_hosts = ["*"]
        self.add_asgi_middleware(
            TrustedHostMiddleware, allowed_hosts=allowed_hosts
        )
        if enable_cors:
            cors_config = {**DEFAULT_CORS_CONFIG, **(cors_config or {})}
            self.add_asgi_middleware(CORSMiddleware, **cors_config)
        if enable_hsts:
            self.add_asgi_middleware(HTTPSRedirectMiddleware)
        if enable_gzip:
            self.add_asgi_middleware(GZipMiddleware, minimum_size=gzip_min_size)

    @property
    def debug(self) -> bool:
        return self._debug

    @debug.setter
    def debug(self, debug: bool):
        self._debug = debug
        self.exception_middleware.debug = debug
        self.server_error_middleware.debug = debug

    @property
    def media_type(self) -> str:
        """The media type configured when instanciating the application."""
        return self._media_type

    @media_type.setter
    def media_type(self, media_type: str):
        if media_type not in self.media_handlers:
            raise UnsupportedMediaType(media_type, handlers=self.media_handlers)
        self._media_type = media_type

    def build_client(self, **kwargs) -> TestClient:
        return TestClient(self, **kwargs)

    def get_template_globals(self):
        # DEPRECATED: 0.13.0
        return {"url_for": self.url_for}

    def url_for(self, name: str, **kwargs) -> str:
        # Implement route name lookup accross sub-apps.
        try:
            return super().url_for(name, **kwargs)
        except HTTPError as exc:
            app_name, _, name = name.partition(":")

            if not app_name:
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

        # Parameters
        prefix (str): A path prefix where the app should be mounted, e.g. `"/myapp"`.
        app: An object implementing [WSGI](https://wsgi.readthedocs.io) or [ASGI](https://asgi.readthedocs.io) protocol.
        """
        if not prefix.startswith("/"):
            prefix = "/" + prefix

        self._prefix_to_app[prefix] = app

        if isinstance(app, App) and app.name is not None:
            self._name_to_prefix_and_app[app.name] = (prefix, app)

    def recipe(self, recipe: "Recipe"):
        """Apply a recipe.

        # Parameters
        recipe (Recipe or RecipeBook):
            a recipe to be applied to the application.

        # See Also
        - [Recipes](../guides/agnostic/recipes.md)
        """
        recipe.apply(self)

    def add_error_handler(self, exception_cls: Type[_E], handler: ErrorHandler):
        """Register a new error handler.

        # Parameters
        exception_cls (Exception class):
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

        middleware_cls (Middleware class):
            A subclass of `bocadillo.Middleware`.

        # See Also
        - [Middleware](../guides/http/middleware.md)
        """
        self.exception_middleware.app = middleware_cls(
            self.exception_middleware.app, **kwargs
        )

    def add_asgi_middleware(self, middleware_cls, *args, **kwargs):
        """Register an ASGI middleware class.

        # Parameters
        middleware_cls (Middleware class):
            A class that complies with the ASGI specification.

        # See Also
        - [ASGI middleware](../guides/agnostic/asgi-middleware.md)
        - [ASGI](https://asgi.readthedocs.io)
        """
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
        else:
            self._lifespan.add_event_handler(event, handler)
            return handler

    async def dispatch_http(self, receive: Receive, send: Send, scope: Scope):
        req = Request(scope, receive)
        res = Response(
            req,
            media_type=self.media_type,
            media_handler=self.media_handlers[self.media_type],
        )
        response = await self.server_error_middleware(req, res)

        await response(receive, send)

        # Re-raise the exception to allow the server to log the error
        # and for the test client to optionally re-raise it too.
        self.server_error_middleware.raise_if_exception()

    async def dispatch_websocket(
        self, receive: Receive, send: Send, scope: Scope
    ):
        await self.websocket_router(scope, receive, send)

    def dispatch(self, scope: Scope) -> ASGIAppInstance:
        if scope["type"] == "websocket":
            return partial(self.dispatch_websocket, scope=scope)
        assert scope["type"] == "http"
        return partial(self.dispatch_http, scope=scope)

    def __call__(self, scope: Scope) -> ASGIAppInstance:
        if scope["type"] == "lifespan":
            return self._lifespan(scope)

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

        return self.asgi(scope)

    def run(
        self,
        host: str = None,
        port: int = None,
        debug: bool = False,
        log_level: str = "info",
        _run: Callable = None,
        **kwargs,
    ):
        """Serve the application using [uvicorn](https://www.uvicorn.org).

        # Parameters

        host (str):
            The host to bind to.
            Defaults to `"127.0.0.1"` (localhost).
            If not given and `$PORT` is set, `"0.0.0.0"` will be used to
            serve to all known hosts.
        port (int):
            The port to bind to.
            Defaults to `8000` or (if set) the value of the `$PORT` environment
            variable.
        debug (bool):
            Whether to serve the application in debug mode. Defaults to `False`.
        log_level (str):
            A logging level for the debug logger. Must be a logging level
            from the `logging` module. Defaults to `"info"`.
        kwargs (dict):
            Extra keyword arguments that will be passed to the Uvicorn runner.

        # See Also
        - [Configuring host and port](../guides/app.md#configuring-host-and-port)
        - [Debug mode](../guides/app.md#debug-mode)
        - [Uvicorn settings](https://www.uvicorn.org/settings/) for all
        available keyword arguments.
        """
        if _run is None:  # pragma: no cover
            _run = run

        if "PORT" in os.environ:
            port = int(os.environ["PORT"])
            if host is None:
                host = "0.0.0.0"

        if host is None:
            host = "127.0.0.1"

        if port is None:
            port = 8000

        if debug:
            self.debug = True
            reloader = StatReload(get_logger(log_level))
            kwargs = {
                "app": self,
                "host": host,
                "port": port,
                "log_level": log_level,
                "debug": self.debug,
                **kwargs,
            }
            reloader.run(run, kwargs)
        else:
            _run(self, host=host, port=port, **kwargs)


@deprecated(
    since="0.12",
    removal="0.13",
    alternative=("bocadillo.App", "/api/applications.md#App"),
    warn_on_instanciate=True,
)
class API(App):
    """The all-mighty API class. An alias to `App`, nothing more."""
