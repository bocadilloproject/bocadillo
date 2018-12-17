"""Built-in error handlers."""
import traceback
from functools import wraps
from typing import Callable, Optional

from .exceptions import HTTPError
from .request import Request
from .response import Response


def error_to_html(req, res, exc: HTTPError):
    res.status_code = exc.status_code
    res.html = f"<h1>{exc.status_code} {exc.status_phrase}</h1>"


def error_to_media(req, res, exc: HTTPError):
    res.status_code = exc.status_code
    res.media = {"error": exc.status_phrase, "status": exc.status_code}


def error_to_text(req, res, exc: HTTPError):
    res.status_code = exc.status_code
    res.text = exc.status_phrase


ErrorHandler = Callable[[Request, Response, Exception], None]


async def _to_res(
    req: Request, exc: Exception, error_handler: ErrorHandler, **kwargs
) -> Response:
    if isinstance(exc, HTTPError):
        res = Response(req, **kwargs)
        error_handler(req, res, exc)
        if exc.status_code == 500:
            traceback.print_exc()
    else:
        res = await _to_res(req, HTTPError(500), error_handler, **kwargs)
    return res


def convert_exception_to_response(
    dispatch, error_handler: Optional[ErrorHandler] = None, **kwargs
):
    """Wrap call to `dispatch()` to always return an HTTP response."""
    if error_handler is None:
        error_handler = error_to_text

    @wraps(dispatch)
    async def inner(req: Request) -> Response:
        try:
            res = await dispatch(req)
        except Exception as exc:
            res = await _to_res(req, exc, error_handler, **kwargs)
        return res

    return inner
