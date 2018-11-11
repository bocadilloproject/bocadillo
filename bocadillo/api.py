"""The Bocadillo API class."""
import os
from contextlib import contextmanager
from http import HTTPStatus
from typing import (Optional, Tuple, Type, List, Dict, Any, Union, Coroutine)

from asgiref.wsgi import WsgiToAsgi
from jinja2 import FileSystemLoader
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.testclient import TestClient
from uvicorn.main import run, get_logger
from uvicorn.reloaders.statreload import StatReload

from .checks import check_route
from .constants import ALL_HTTP_METHODS
from .cors import DEFAULT_CORS_CONFIG
from .error_handlers import ErrorHandler, handle_http_error
from .exceptions import HTTPError
from .middleware import CommonMiddleware, RoutingMiddleware
from .redirection import Redirection
from .request import Request
from .response import Response
from .route import Route
from .static import static
from .templates import Template, get_templates_environment
from .types import ASGIApp, WSGIApp, ASGIAppInstance


class API:
    """Bocadillo API.

    Parameters
    ----------
    templates_dir : str, optional
        The name of the directory containing templates, relative to
        the application entry point.
        Defaults to 'templates'.
    static_dir: str, optional
        The name of the directory containing static files, relative to
        the application entry point.
        Defaults to 'static'.
    static_root : str, optional
        The path prefix for static assets.
        Defaults to 'static'.
    allowed_hosts : list of str, optional
        A list of hosts which the server is allowed to run at.
        If the list contains '*', any host is allowed.
        Defaults to ['*'].
    enable_cors : bool, optional
        If True, Cross Origin Resource Sharing will be configured according
        to `cors_config`.
        Defaults to False.
    cors_config : dict, optional
        A dictionary of CORS configuration parameters.
        Defaults to `{'allow_origins': [], 'allow_methods': ['GET']}`.
        See also: https://www.starlette.io/middleware/#corsmiddleware
    enable_hsts : bool, optional
        If True, enable HSTS (HTTP Strict Transport Security) and automatically
        redirect HTTP traffic to HTTPS.
        Defaults to False.
    """

    _error_handlers: List[Tuple[Type[Exception], ErrorHandler]]

    def __init__(
            self,
            templates_dir: str = 'templates',
            static_dir: Optional[str] = 'static',
            static_root: Optional[str] = 'static',
            allowed_hosts: List[str] = None,
            enable_cors: bool = False,
            cors_config: dict = None,
            enable_hsts: bool = False,
    ):
        self._routes: Dict[str, Route] = {}
        self._named_routes: Dict[str, Route] = {}

        self._error_handlers = []
        self.add_error_handler(HTTPError, handle_http_error)

        self._templates = get_templates_environment([
            os.path.abspath(templates_dir),
        ])
        self._templates.globals.update(self._get_template_globals())

        self._extra_apps: Dict[str, Any] = {}

        self.client = self._build_client()

        if static_dir is not None:
            if static_root is None:
                static_root = static_dir
            self.mount(static_root, static(static_dir))

        if allowed_hosts is None:
            allowed_hosts = ['*']
        self.allowed_hosts = allowed_hosts

        if cors_config is None:
            cors_config = {}
        self.cors_config = {**DEFAULT_CORS_CONFIG, **cors_config}

        # Middleware
        self._routing_middleware = RoutingMiddleware(self)
        self._common_middleware = CommonMiddleware(self._routing_middleware)
        self.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=self.allowed_hosts,
        )
        if enable_cors:
            self.add_middleware(CORSMiddleware, **self.cors_config)
        if enable_hsts:
            self.add_middleware(HTTPSRedirectMiddleware)

    def _build_client(self) -> TestClient:
        return TestClient(self)

    def mount(self, prefix: str, app: Union[ASGIApp, WSGIApp]):
        """Mount another WSGI or ASGI app at the given prefix."""
        if not prefix.startswith('/'):
            prefix = '/' + prefix
        self._extra_apps[prefix] = app

    def add_error_handler(self, exception_cls: Type[Exception],
                          handler: ErrorHandler):
        """Register a new error handler.

        Parameters
        ----------
        exception_cls : Exception class
            The type of exception that should be handled.
        handler : (request, response, exception) -> None
            The actual error handler, which is called when an instance of
            `exception_cls` is caught.
        """
        self._error_handlers.insert(0, (exception_cls, handler))

    def error_handler(self, exception_cls: Type[Exception]):
        """Register a new error handler (decorator syntax).

        Example
        -------
        >>> import bocadillo
        >>> api = bocadillo.API()
        >>> @api.error_handler(KeyError)
        ... def on_key_error(req, resp, exc):
        ...     pass  # perhaps set resp.content and resp.status_code
        """

        def wrapper(handler):
            self.add_error_handler(exception_cls, handler)
            return handler

        return wrapper

    def _find_handlers(self, exception):
        return (
            handler for err_type, handler in self._error_handlers
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
            break
        else:
            raise exception from None

    def route(self, pattern: str, *, methods: List[str] = None,
              name: str = None):
        """Register a new route.

        Parameters
        ----------
        pattern : str
            A route pattern given as an f-string expression.
        methods : list of str, optional
            HTTP methods supported by this route.
            Defaults to all HTTP methods.
            Ignored for class-based views.
        name : str, optional
            A name for this route, which must be unique.

        Example
        -------
        >>> import bocadillo
        >>> api = bocadillo.API()
        >>> @api.route('/greet/{person}')
        ... def greet(req, resp, person: str):
        ...     pass
        """
        if methods is None:
            methods = ALL_HTTP_METHODS

        methods = [method.upper() for method in methods]

        def wrapper(view):
            check_route(pattern, view, methods)
            route = Route(
                pattern=pattern,
                view=view,
                methods=methods,
                name=name,
            )

            self._routes[pattern] = route
            if name is not None:
                self._named_routes[name] = route

            return route

        return wrapper

    def _find_matching_route(self, path: str) -> Tuple[Optional[str], dict]:
        """Find a route matching the given path."""
        for pattern, route in self._routes.items():
            kwargs = route.match(path)
            if kwargs is not None:
                return pattern, kwargs
        return None, {}

    def _get_route_or_404(self, name: str):
        try:
            return self._named_routes[name]
        except KeyError as e:
            raise HTTPError(HTTPStatus.NOT_FOUND.value) from e

    def url_for(self, name: str, **kwargs) -> str:
        """Return the URL path for a route.

        Parameters
        ----------
        name : str
            Name of the route.
        kwargs :
            Route parameters.

        Raises
        ------
        HTTPError(404) :
            If no route exists for the given `name`.
        """
        route = self._get_route_or_404(name)
        return route.url(**kwargs)

    def redirect(self, *,
                 name: str = None,
                 url: str = None,
                 permanent: bool = False,
                 **kwargs):
        """Redirect to another route.

        Parameters
        ----------
        name : str, optional
            Name of the route to redirect to.
        url : str, optional (unless name not given)
            URL of the route to redirect to.
        permanent : bool, optional
            If False (the default), returns a temporary redirection (302).
            If True, returns a permanent redirection (301).
        kwargs :
            Route parameters.
        """
        if name is not None:
            url = self.url_for(name=name, **kwargs)
        else:
            assert url is not None, 'url is expected if no route name is given'
        raise Redirection(url=url, permanent=permanent)

    def _get_template_globals(self) -> dict:
        return {
            'url_for': self.url_for,
        }

    @property
    def templates_dir(self) -> str:
        loader: FileSystemLoader = self._templates.loader
        return loader.searchpath[0]

    @templates_dir.setter
    def templates_dir(self, templates_dir: str):
        loader: FileSystemLoader = self._templates.loader
        loader.searchpath = [os.path.abspath(templates_dir)]

    def _get_template(self, name: str) -> Template:
        return self._templates.get_template(name)

    @contextmanager
    def _prevent_async_template_rendering(self):
        """If enabled, temporarily disable async template rendering.

        Notes
        -----
        Hot fix for a bug with Jinja2's async environment, which always
        renders asynchronously even under `render()`.
        Example error:
        `RuntimeError: There is no current event loop in thread [...]`
        """
        if not self._templates.is_async:
            yield
            return

        self._templates.is_async = False
        try:
            yield
        finally:
            self._templates.is_async = True

    @staticmethod
    def _prepare_context(context: dict = None, **kwargs):
        if context is None:
            context = {}
        context.update(kwargs)
        return context

    async def template(self, name_: str,
                       context: dict = None, **kwargs) -> Coroutine:
        """Render a template asynchronously.

        Can only be used within `async`  functions.

        Parameters
        ----------
        name_ : str
            Name of the template, located inside `templates_dir`.
            Trailing underscore to avoid collisions with a potential
            context variable named 'name'.
        context : dict
            Context variables to inject in the template.
        """
        context = self._prepare_context(context, **kwargs)
        return await self._get_template(name_).render_async(context)

    def template_sync(self, name_: str, context: dict = None, **kwargs) -> str:
        """Render a template synchronously.

        See Also
        --------
        .template()
        """
        context = self._prepare_context(context, **kwargs)
        with self._prevent_async_template_rendering():
            return self._get_template(name_).render(context)

    def template_string(self, source: str, context: dict = None,
                        **kwargs) -> str:
        """Render a template from a string (synchronous)."""
        context = self._prepare_context(context, **kwargs)
        with self._prevent_async_template_rendering():
            template = self._templates.from_string(source=source)
            return template.render(context)

    def run(self,
            host: str = None,
            port: int = None,
            debug: bool = False,
            log_level: str = 'info'):
        """Serve the application using uvicorn.

        Parameters
        ----------
        host : str, optional
            The host to bind to.
            Defaults to '127.0.0.1' (localhost). If not given and `PORT` is set,
            '0.0.0.0' will be used to serve to all known hosts.
        port : int, optional
            The port to bind to.
            Defaults to 8000 or (if set) the value of the `PORT` environment
            variable.
        debug : bool, optional
            Whether to serve the application in debug mode. Defaults to `False`.
        log_level : str, optional
            A logging level for the debug logger. Must be compatible with
            logging levels from the `logging` module.

        See Also
        --------
        https://www.uvicorn.org/settings/
        """
        if 'PORT' in os.environ:
            port = int(os.environ['PORT'])
            if host is None:
                host = '0.0.0.0'

        if host is None:
            host = '127.0.0.1'

        if port is None:
            port = 8000

        if debug:
            reloader = StatReload(get_logger(log_level))
            reloader.run(run, {
                'app': self,
                'host': host,
                'port': port,
                'log_level': log_level,
                'debug': debug,
            })
        else:
            run(self, host=host, port=port)

    async def dispatch(self, request: Request) -> Response:
        """Dispatch a request and return a response."""
        response = Response(request)

        try:
            pattern, kwargs = self._find_matching_route(request.url.path)
            route = self._routes.get(pattern)
            if route is None:
                raise HTTPError(status=404)
            else:
                try:
                    await route(request, response, **kwargs)
                except Redirection as redirection:
                    response = redirection.response
        except Exception as e:
            self._handle_exception(request, response, e)

        return response

    def _is_routing_middleware(self, middleware_cls) -> bool:
        return hasattr(middleware_cls, 'dispatch')

    def add_middleware(self, middleware_cls, **kwargs):
        if self._is_routing_middleware(middleware_cls):
            self._routing_middleware.add(middleware_cls, **kwargs)
        else:
            self._common_middleware.add(middleware_cls, **kwargs)

    def _find_app(self, scope: dict) -> ASGIAppInstance:
        """Return an ASGI app depending on the scope's path."""
        path: str = scope['path']

        # Return a sub-mounted extra app, if found
        for prefix, app in self._extra_apps.items():
            if not path.startswith(prefix):
                continue
            # Remove prefix from path so that the request is made according
            # to the mounted app's point of view.
            scope['path'] = path[len(prefix):]
            try:
                return app(scope)
            except TypeError:
                app = WsgiToAsgi(app)
                return app(scope)

        return self._common_middleware(scope)

    def __call__(self, scope: dict) -> ASGIAppInstance:
        return self._find_app(scope)
