from typing import Optional

from .app_types import HTTPApp
from .request import Request
from .response import Response
from ..compat import call_async


class Middleware(HTTPApp):
    """Base class for middleware classes.

    # Parameters
    dispatch (coroutine function):
        a function whose return value can be awaited to obtain a response.
    kwargs (dict):
        Keyword arguments passed when registering the middleware.
    """

    def __init__(self, app: HTTPApp, **kwargs):
        self.app = app
        self.kwargs = kwargs

    async def before_dispatch(
        self, req: Request, res: Response
    ) -> Optional[Response]:
        """Perform processing before a request is dispatched.

        If the `Response` object is returned, it will be used
        and no further processing will be performed.

        # Parameters
        req (Request): a Request object.
        res (Response): a Response object.
        """

    async def after_dispatch(
        self, req: Request, res: Response
    ) -> Optional[Response]:
        """Perform processing after a request has been dispatched.

        If the `Response` object is returned, it is used instead of the response
        obtained by awaiting `dispatch()`.

        # Parameters
        req (Request): a Request object.
        res (Response): a Response object.
        """

    async def process(self, req: Request, res: Response):
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
        before_res = await call_async(self.before_dispatch, req, res)
        if before_res:
            return before_res

        res = await self.app(req, res)

        after_res = await call_async(self.after_dispatch, req, res)
        if after_res:
            return after_res

        return res

    async def __call__(self, req: Request, res: Response) -> Response:
        return await self.process(req, res)
