"""The Bocadillo API class."""
import os
from contextlib import contextmanager
from typing import Optional, Tuple, Type, List, Callable

import uvicorn

from .request import Request
from .response import Response
from .route import Route

ErrorHandler = Callable[[Request, Response, Exception], None]


class API:
    """Bocadillo API."""

    def __init__(self):
        self._routes = {}
        self._error_handlers: List[Tuple[Type[Exception], ErrorHandler]] = []

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
        """Register a new error handler (decorator syntax)."""

        def wrapper(handler):
            self.add_error_handler(exception_cls, handler)
            return handler

        return wrapper

    def route(self, pattern: str):
        """Register a new route."""

        def wrapper(handler):
            route = Route(pattern=pattern, view=handler)
            # TODO check that no route already exists for pattern
            self._routes[pattern] = route
            return route

        return wrapper

    async def _dispatch(self, request) -> Response:
        """Dispatch a request and return a response."""
        response = Response(request)

        try:
            pattern, kwargs = self._find_route(request.url.path)
            route = self._routes.get(pattern)
            if route is None:
                # TODO HTTPError(status=404)
                raise ValueError('Not found')
            else:
                await route(request, response, **kwargs)
        except Exception as e:
            self._handle_exception(request, response, e)

        return response

    def _find_route(self, path: str) -> Tuple[Optional[str], dict]:
        """Find a route matching the given path."""
        print(path)
        for pattern, route in self._routes.items():
            kwargs = route.match(path)
            if kwargs is not None:
                return pattern, kwargs
        return None, {}

    def _find_handlers(self, exception):
        return (
            handler for err_type, handler in self._error_handlers
            if isinstance(exception, err_type)
        )

    def _handle_exception(self, request, response, exception) -> None:
        """Handle an exception raised during dispatch.

        If no handler was registered for the exception, it is escalated.
        """
        handled = False

        for handler in self._find_handlers(exception):
            handler(request, response, exception)
            handled = True

        if not handled:
            raise exception

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
