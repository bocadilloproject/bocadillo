"""The Bocadillo API class."""
import os
from functools import partial
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from asgiref.wsgi import WsgiToAsgi
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.testclient import TestClient
from uvicorn.main import get_logger, run
from uvicorn.reloaders.statreload import StatReload

from .cors import DEFAULT_CORS_CONFIG
from .error_handlers import ErrorHandler, convert_exception_to_response
from .exceptions import HTTPError
from .hooks import HooksMixin
from .media import Media
from .meta import APIMeta
from .recipes import RecipeBase
from .redirection import Redirection
from .request import Request
from .response import Response
from .routing import RoutingMixin
from .static import static
from .templates import TemplatesMixin
from .types import ASGIApp, ASGIAppInstance, WSGIApp


class API(TemplatesMixin, RoutingMixin, HooksMixin, metaclass=APIMeta):
    """The all-mighty API class.

    This class implements the [ASGI](https://asgi.readthedocs.io) protocol.

    # Example

    ```python
    >>> import bocadillo
    >>> api = bocadillo.API()
    ```

    # Parameters

    templates_dir (str):
        The name of the directory where templates are searched for,
        relative to the application entry point.
        Defaults to `"templates"`.
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
        See also [CORS](../topics/features/cors.md).
    cors_config (dict):
        A dictionary of CORS configuration parameters.
        Defaults to `dict(allow_origins=[], allow_methods=["GET"])`.
    enable_hsts (bool):
        If `True`, enable HSTS (HTTP Strict Transport Security) and automatically
        redirect HTTP traffic to HTTPS.
        Defaults to `False`.
        See also [HSTS](../topics/features/hsts.md).
    enable_gzip (bool):
        If `True`, enable GZip compression and automatically
        compress responses for clients that support it.
        Defaults to `False`.
        See also [GZip](../topics/features/gzip.md).
    gzip_min_size (int):
        If specified, compress only responses that
        have more bytes than the specified value.
        Defaults to `1024`.
    media_type (str):
        Determines how values given to `res.media` are serialized.
        Can be one of the supported media types.
        Defaults to `"application/json"`.
        See also [Media](../topics/request-handling/media.md).
    """

    _error_handlers: List[Tuple[Type[Exception], ErrorHandler]]

    def __init__(
        self,
        templates_dir: str = "templates",
        static_dir: Optional[str] = "static",
        static_root: Optional[str] = "static",
        allowed_hosts: List[str] = None,
        enable_cors: bool = False,
        cors_config: dict = None,
        enable_hsts: bool = False,
        enable_gzip: bool = False,
        gzip_min_size: int = 1024,
        media_type: Optional[str] = Media.JSON,
    ):
        super().__init__(templates_dir=templates_dir)

        self._error_handlers = []

        self._extra_apps: Dict[str, Any] = {}

        self.client = self._build_client()

        if static_dir is not None:
            if static_root is None:
                static_root = static_dir
            self.mount(static_root, static(static_dir))

        self._media = Media(media_type=media_type)

        self._middleware = []
        self._asgi_middleware = []

        if allowed_hosts is None:
            allowed_hosts = ["*"]
        self.add_asgi_middleware(
            TrustedHostMiddleware, allowed_hosts=allowed_hosts
        )

        if enable_cors:
            if cors_config is None:
                cors_config = {}
            cors_config = {**DEFAULT_CORS_CONFIG, **cors_config}
            self.add_asgi_middleware(CORSMiddleware, **cors_config)

        if enable_hsts:
            self.add_asgi_middleware(HTTPSRedirectMiddleware)

        if enable_gzip:
            self.add_asgi_middleware(GZipMiddleware, minimum_size=gzip_min_size)

    def get_template_globals(self):
        return {"url_for": self.url_for}

    def _build_client(self) -> TestClient:
        return TestClient(self)

    def mount(self, prefix: str, app: Union[ASGIApp, WSGIApp]):
        """Mount another WSGI or ASGI app at the given prefix.

        # Parameters
        prefix (str): A path prefix where the app should be mounted, e.g. `"/myapp"`.
        app: An object implementing [WSGI](https://wsgi.readthedocs.io) or [ASGI](https://asgi.readthedocs.io) protocol.
        """
        if not prefix.startswith("/"):
            prefix = "/" + prefix
        self._extra_apps[prefix] = app

    def recipe(self, recipe: RecipeBase):
        recipe.apply(self)

    @property
    def media_type(self) -> str:
        """The currently configured media type.

        When setting it to a value outside of built-in or custom media types,
        an `UnsupportedMediaType` exception is raised.
        """
        return self._media.type

    @media_type.setter
    def media_type(self, media_type: str):
        self._media.type = media_type

    @property
    def media_handlers(self) -> dict:
        """The dictionary of supported media handlers.

        You can access, edit or replace this at will.
        """
        return self._media.handlers

    @media_handlers.setter
    def media_handlers(self, media_handlers: dict):
        self._media.handlers = media_handlers

    def add_error_handler(
        self, exception_cls: Type[Exception], handler: ErrorHandler
    ):
        """Register a new error handler.

        # Parameters
        exception_cls (Exception class):
            The type of exception that should be handled.
        handler (callable):
            The actual error handler, which is called when an instance of
            `exception_cls` is caught.
            Should accept a `req`, a `res` and an `exc`.
        """
        self._error_handlers.insert(0, (exception_cls, handler))

    def error_handler(self, exception_cls: Type[Exception]):
        """Register a new error handler (decorator syntax).

        # Example
        ```python
        >>> import bocadillo
        >>> api = bocadillo.API()
        >>> @api.error_handler(KeyError)
        ... def on_key_error(req, res, exc):
        ...     pass  # perhaps set res.content and res.status_code
        ```
        """

        def wrapper(handler):
            self.add_error_handler(exception_cls, handler)
            return handler

        return wrapper

    def _find_handlers(self, exception):
        return (
            handler
            for err_type, handler in self._error_handlers
            if isinstance(exception, err_type)
        )

    def _handle_exception(self, request, response, exception) -> None:
        """Handle an exception raised during dispatch.

        At most one handler is called for the exception: the first one
        to support it.

        If no handler was registered for the exception, it is raised.
        """
        for handler in self._find_handlers(exception):
            handler(request, response, exception)
            if response.status_code is None:
                response.status_code = 500
            break
        else:
            raise exception from None

    def redirect(
        self,
        *,
        name: str = None,
        url: str = None,
        permanent: bool = False,
        **kwargs
    ):
        """Redirect to another route.

        # Parameters
        name (str): name of the route to redirect to.
        url (str): URL of the route to redirect to, required if `name` is ommitted.
        permanent (bool):
            If `False` (the default), returns a temporary redirection (302).
            If `True`, returns a permanent redirection (301).
        kwargs (dict):
            Route parameters.

        # Raises
        Redirection: an exception that will be caught by #API.dispatch().
        """
        if name is not None:
            url = self.url_for(name=name, **kwargs)
        else:
            assert url is not None, "url is expected if no route name is given"
        raise Redirection(url=url, permanent=permanent)

    def add_middleware(self, middleware_cls, **kwargs):
        """Register a middleware class.

        See also [Middleware](../topics/features/middleware.md).

        # Parameters

        middleware_cls (Middleware class):
            A subclass of #~some.middleware.Middleware.
        """
        self._middleware.insert(0, (middleware_cls, kwargs))

    def add_asgi_middleware(self, middleware_cls, *args, **kwargs):
        """Register an ASGI middleware class.

        # Parameters

        middleware_cls (Middleware class):
            A class that conforms to ASGI standard.
        """
        self._asgi_middleware.insert(0, (middleware_cls, args, kwargs))

    async def dispatch(self, req: Request) -> Response:
        """Dispatch a req and return a response.

        For the exact algorithm, see
        [How are requests processed?](../topics/request-handling/routes-url-design.md#how-are-requests-processed).

        # Parameters
        req (Request): an inbound HTTP request.

        # Returns
        response (Response): an HTTP response.
        """

        res = Response(req, media=self._media)

        try:
            match = self._router.match(req.url.path)
            if match is None:
                raise HTTPError(status=404)

            route, params = match.route, match.params
            route.raise_for_method(req)

            try:
                hooks = self.get_hooks().on(route, req, res, params)
                async with hooks:
                    await route(req, res, **params)
            except Redirection as redirection:
                res = redirection.response

        except Exception as e:
            self._handle_exception(req, res, e)

        return res

    def find_app(self, scope: dict) -> ASGIAppInstance:
        """Return the ASGI application suited to the given ASGI scope.

        This is also what `API.__call__(self)` returns.

        # Parameters
        scope (dict):
            An ASGI scope.

        # Returns
        app:
            An ASGI application instance
            (either `self` or an instance of a sub-app).
        """
        path: str = scope["path"]

        # Return a sub-mounted extra app, if found
        for prefix, app in self._extra_apps.items():
            if not path.startswith(prefix):
                continue
            # Remove prefix from path so that the request is made according
            # to the mounted app's point of view.
            scope["path"] = path[len(prefix) :]
            try:
                return app(scope)
            except TypeError:
                app = WsgiToAsgi(app)
                return app(scope)

        def app(s: dict):
            async def asgi(receive, send):
                nonlocal s
                req = Request(s, receive)
                res = await self._get_response(req)
                await res(receive, send)

            return asgi

        app = self._asgi_middleware_chain(app)
        return app(scope)

    async def _get_response(self, req: Request) -> Response:
        convert = partial(convert_exception_to_response, media=self._media)
        dispatch = convert(self.dispatch)
        for cls, kwargs in self._middleware:
            middleware = cls(dispatch, **kwargs)
            dispatch = convert(middleware)
        return await dispatch(req)

    def _asgi_middleware_chain(self, app: ASGIApp) -> ASGIApp:
        for middleware_cls, args, kwargs in self._asgi_middleware:
            app: ASGIApp = middleware_cls(app, *args, **kwargs)
        return app

    def run(
        self,
        host: str = None,
        port: int = None,
        debug: bool = False,
        log_level: str = "info",
    ):
        """Serve the application using [uvicorn](https://www.uvicorn.org).

        For further details, refer to
        [uvicorn settings](https://www.uvicorn.org/settings/).

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
        """
        if "PORT" in os.environ:
            port = int(os.environ["PORT"])
            if host is None:
                host = "0.0.0.0"

        if host is None:
            host = "127.0.0.1"

        if port is None:
            port = 8000

        if debug:
            reloader = StatReload(get_logger(log_level))
            reloader.run(
                run,
                {
                    "app": self,
                    "host": host,
                    "port": port,
                    "log_level": log_level,
                    "debug": debug,
                },
            )
        else:
            run(self, host=host, port=port)

    def __call__(self, scope: dict) -> ASGIAppInstance:
        return self.find_app(scope)
