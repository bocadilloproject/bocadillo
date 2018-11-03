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

    def run(self, host='0.0.0.0', port=5200):
        """Run the development server."""
        print(f'Serving Bocadillo on {host}:{port}')
        uvicorn.run(self, host=host, port=port)

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
