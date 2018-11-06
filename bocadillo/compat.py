from .types import WSGIApp


def empty_wsgi_app() -> WSGIApp:
    """Return a WSGI app that always returns 404 Not Found."""

    def wsgi(environ, start_response):
        status = '404 Not Found'
        body = b'Not Found'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [body]

    return wsgi
