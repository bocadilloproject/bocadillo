"""The Bocadillo API class."""
import os
from typing import Optional, Tuple

import uvicorn
from starlette.requests import Request

from bocadillo.routing import Route
from .response import Response


class API:
    """Bocadillo API."""

    def __init__(self):
        self._routes = {}

    def route(self, pattern: str):
        """Register a new route."""

        def wrapper(handler):
            route = Route(pattern=pattern, handler=handler)
            # TODO check that no route already exists for pattern
            self._routes[pattern] = route
            return route

        return wrapper

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
            Defaults to 5050 or (if set) the value of the `PORT` environment
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
            port = 5050

        print(f'Serving Bocadillo on {host}:{port}')
        uvicorn.run(self, host=host, port=port, debug=debug)

    def _find_route(self, path: str) -> Tuple[Optional[str], dict]:
        for pattern, route in self._routes.items():
            kwargs = route.match(path)
            if kwargs is not None:
                return pattern, kwargs
        return None, {}

    @staticmethod
    def _default_response(request, response):
        response.content = 'Not Found'
        response.status_code = 404

    async def _dispatch(self, request, receive, send) -> Response:
        """Dispatch a request to the router."""
        response = Response(request)

        pattern, kwargs = self._find_route(request.url.path)
        route = self._routes.get(pattern)

        if route is not None:
            await route(request, response, **kwargs)
        else:
            self._default_response(request, response)

        return response

    def asgi(self, scope):
        """Return a new ASGI application.

        See Also
        --------
        https://github.com/encode/uvicorn
        """

        async def asgi(receive, send):
            nonlocal scope
            request = Request(scope, receive)
            response = await self._dispatch(request, receive=receive, send=send)
            await response(receive, send)

        return asgi

    def __call__(self, scope):
        return self.asgi(scope)
