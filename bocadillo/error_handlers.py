"""Built-in error handlers."""

from bocadillo.exceptions import HTTPError


def handle_http_error(_, response, exception: HTTPError):
    response.status_code = exception.status_code
    response.text = exception.status_phrase
