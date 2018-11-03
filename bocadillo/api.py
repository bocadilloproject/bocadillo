"""The Bocadillo API class."""
import os

import uvicorn
from starlette.requests import Request
from starlette.responses import Response


class API:
    """Bocadillo API."""

    def route(self, pattern: str):
        """Register a new route."""

        def decorated(handler):
            # TODO: register handler on the router
            return handler

        return decorated

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

    async def _dispatch(self, req, receive, send) -> Response:
        """Dispatch a request to the router."""
        # TODO use registered routes
        content = f'{req.method} {req.url.path}'
        response = Response(content, media_type='text/plain')
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
