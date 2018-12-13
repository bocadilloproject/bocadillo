"""Bocadillo middleware definition."""
from typing import Coroutine, Callable

from bocadillo.compat import call_async
from bocadillo.response import Response
from .request import Request


Dispatcher = Callable[[Request], Coroutine]


class Middleware:
    """Base class for middleware classes."""

    def __init__(self, dispatch: Dispatcher, **kwargs):
        self.dispatch = dispatch
        self.kwargs = kwargs

    async def __call__(self, req: Request) -> Response:
        res: Response = None

        if hasattr(self, "before_dispatch"):
            res = await call_async(self.before_dispatch, req)

        res = res or await self.dispatch(req)

        if hasattr(self, "after_dispatch"):
            res = await call_async(self.after_dispatch, req, res) or res

        return res


# TODO: remove in v0.8
RoutingMiddleware = Middleware
