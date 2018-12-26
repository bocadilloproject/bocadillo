"""Bocadillo middleware definition."""
from typing import Callable, Awaitable

from .compat import call_async
from .request import Request
from .response import Response

Dispatcher = Callable[[Request], Awaitable[Response]]


class Middleware:
    """Base class for middleware classes.

    # Parameters
    dispatch (coroutine function):
        a function whose return value can be awaited to obtain a response.
    kwargs (dict):
        Keyword arguments passed when registering the middleware.
    """

    def __init__(self, dispatch: Dispatcher, **kwargs):
        self.dispatch = dispatch
        self.kwargs = kwargs

    async def before_dispatch(self, req: Request):
        """Perform processing before a request is dispatched.

        If a `Response` object is returned, it will be used
        and no further processing will be performed.

        # Parameters
        req (Request): a Request object.
        """

    async def after_dispatch(self, req: Request, res: Response):
        """Perform processing after a request has been dispatched.

        If a `Response` object is returned, it is used instead of the response
        obtained by awaiting `dispatch()`.

        # Parameters
        req (Request): a Request object.
        res (Response): a Response object.
        """

    async def process(self, req: Request) -> Response:
        """Process an incoming request.

        Roughly equivalent to:

        ```python
        res = await self.before_dispatch(req) or None
        res = res or await self.dispatch(req)
        res = await self.after_dispatch(req, res) or res
        return res
        ```

        Aliased by `__call__()`.

        # Parameters
        req (Request): a request object.

        # Returns
        res (Response): a Response object.
        """
        res = await call_async(self.before_dispatch, req) or None
        res = res or await self.dispatch(req)
        res = await call_async(self.after_dispatch, req, res) or res
        return res

    async def __call__(self, req: Request) -> Response:
        return await self.process(req)


# TODO: remove in v0.8
RoutingMiddleware = Middleware
