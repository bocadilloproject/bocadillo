"""The Bocadillo API class."""
import os
from pathlib import Path
from typing import Optional, Tuple, Type, List, Callable, Dict

import uvicorn
from jinja2 import FileSystemLoader

from .constants import ALL_HTTP_METHODS
from .http_error import HTTPError, handle_http_error
from .request import Request
from .response import Response
from .route import Route
from .templates import Template, get_templates_environment

ErrorHandler = Callable[[Request, Response, Exception], None]


class API:
    """Bocadillo API.

    Parameters
    ----------
    templates_dir : str, optional
        The name of the directory containing templates, relative to
        the application entry point.
        Defaults to 'templates'.
    """

    _error_handlers: List[Tuple[Type[Exception], ErrorHandler]]

    def __init__(self, templates_dir: str = 'templates'):
        self._routes: Dict[str, Route] = {}
        self._error_handlers = []
        self.add_error_handler(HTTPError, handle_http_error)
        templates_location = str(Path(os.path.abspath(templates_dir)))
        self._templates = get_templates_environment([templates_location])

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

    def route(self, pattern: str, *, methods: List[str] = None):
        """Register a new route.

        Parameters
        ----------
        pattern : str
            A route pattern given as an f-string expression.
        methods : list of str
            HTTP methods supported by this route.
            Defaults to all HTTP methods.
            Ignored for class-based views.

        Example
        -------
        >>> import bocadillo
        >>> api = bocadillo.API()
        >>> @api.route('/greet/{person}')
        ... def greet(req, resp, person: str):
        ...     pass
        """
        assert pattern not in self._routes, (
            f'Pattern "{pattern}" already registered on route '
            f'"{self._routes[pattern].name}".'
        )

        if methods is None:
            methods = ALL_HTTP_METHODS

        methods = [method.upper() for method in methods]

        for method in methods:
            assert method in ALL_HTTP_METHODS, (
                f'{method} is not one of the valid HTTP methods: '
                f'{", ".join(ALL_HTTP_METHODS)}'
            )

        def wrapper(view):
            route = Route(
                pattern=pattern,
                view=view,
                methods=methods,
            )
            self._routes[pattern] = route
            return route

        return wrapper

    def _find_route(self, path: str) -> Tuple[Optional[str], dict]:
        """Find a route matching the given path."""
        for pattern, route in self._routes.items():
            kwargs = route.match(path)
            if kwargs is not None:
                return pattern, kwargs
        return None, {}

    async def _dispatch(self, request) -> Response:
        """Dispatch a request and return a response."""
        response = Response(request)

        try:
            pattern, kwargs = self._find_route(request.url.path)
            route = self._routes.get(pattern)
            if route is None:
                raise HTTPError(status=404)
            else:
                await route(request, response, **kwargs)
        except Exception as e:
            self._handle_exception(request, response, e)

        return response

    @property
    def templates_dir(self) -> str:
        loader: FileSystemLoader = self._templates.loader
        return loader.searchpath[0]

    def _get_template(self, name: str) -> Template:
        return self._templates.get_template(name)

    def template(self, name: str, **context):
        """Render a template.

        Parameters
        ----------
        name : str
            Name of the template, located inside `templates_dir`.
        context : dict
            Context variables to inject in the template.
        """
        return self._get_template(name).render(**context)

    async def template_async(self, name: str, **context):
        """Render a template asynchronously.

        Can only be used within `async`  functions.

        See Also
        --------
        .template()
        """
        return await self._get_template(name).render_async(**context)

    def run(self, host: str = None, port: int = None, debug: bool = False):
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

        uvicorn.run(self, host=host, port=port, debug=debug)

    def as_asgi(self, scope):
        """Return a new ASGI application.

        See Also
        --------
        https://github.com/encode/uvicorn
        """

        async def asgi_app(receive, send):
            nonlocal scope
            request = Request(scope, receive)
            response = await self._dispatch(request)
            await response(receive, send)

        return asgi_app

    def __call__(self, scope):
        return self.as_asgi(scope)
