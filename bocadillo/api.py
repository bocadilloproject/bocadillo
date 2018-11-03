"""The Bocadillo API class."""


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
        print(f'Bocadillo serving on {host}:{port}')
        # TODO
