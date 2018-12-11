"""Built-in error handlers."""
import traceback
from functools import wraps
from typing import Callable

from .exceptions import HTTPError
from .request import Request
from .response import Response


def _handle_http_error(req, res, exc: HTTPError):
    res.status_code = exc.status_code
    res.html = f"<h1>{exc.status_code} {exc.status_phrase}</h1>"


ErrorHandler = Callable[[Request, Response, Exception], None]


async def _res_for_exc(req: Request, exc: Exception, **kwargs):
    if isinstance(exc, HTTPError):
        res = Response(req, **kwargs)
        _handle_http_error(req, res, exc)
        if exc.status_code == 500:
            traceback.print_exc()
    else:
        res = await _res_for_exc(req, HTTPError(500), **kwargs)
    return res


def convert_exception_to_response(dispatch, **kwargs):
    @wraps(dispatch)
    async def inner(req: Request):
        try:
            res = await dispatch(req)
        except Exception as exc:
            res = await _res_for_exc(req, exc, **kwargs)
        return res

    return inner
