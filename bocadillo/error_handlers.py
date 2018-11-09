"""Built-in error handlers."""

from bocadillo.exceptions import HTTPError


def handle_http_error(_, res, exc: HTTPError):
    res.status_code = exc.status_code
    res.html = f'<h1>{exc.status_code} {exc.status_phrase}</h1>'
