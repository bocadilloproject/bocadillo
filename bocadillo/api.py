"""The Bocadillo API class."""
import uvicorn


class API:
    """Bocadillo API."""

    def route(self, pattern: str):
        """Register a new route."""
        def decorated(handler):
            # TODO: register handler on the router
            return handler
        return decorated

    def serve(self, host: str, port: int):
        """Serve the application."""
        print(f'Serving Bocadillo on {host}:{port}')
        uvicorn.run(self, host=host, port=port)

    def run(self, **kwargs):
        return self.serve(**kwargs)

    def asgi(self, scope):
        """Return a new ASGI application.

        See Also
        --------
        https://github.com/encode/uvicorn
        """
        async def asgi(receive, send):
            # TODO
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    [b'content-type', b'text/plain'],
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': b'Hello, Bocadillo!',
            })

        return asgi

    def __call__(self, scope):
        return self.asgi(scope)
