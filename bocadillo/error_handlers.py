"""Built-in error handlers."""
from typing import Callable

from .exceptions import HTTPError
from .request import Request
from .response import Response


def handle_http_error(_, res, exc: HTTPError):
    res.status_code = exc.status_code
    res.html = f'<h1>{exc.status_code} {exc.status_phrase}</h1>'


ErrorHandler = Callable[[Request, Response, Exception], None]
