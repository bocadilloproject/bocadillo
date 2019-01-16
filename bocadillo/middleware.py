from typing import Optional, Awaitable

from .app_types import HTTPApp
from .compat import call_async
from .request import Request
from .response import Response


class Middleware(HTTPApp):
    """Base class for middleware classes.

    # Parameters
    app: a function that may as well be another `Middleware` instance.
    kwargs (any):
        Keyword arguments passed when registering the middleware on the API.
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

        # Returns
        res (Response or None): an optional response object.
        """

    async def after_dispatch(
        self, req: Request, res: Response
    ) -> Optional[Response]:
        """Perform processing after a request has been dispatched.

        # Parameters
        req (Request): a Request object.
        res (Response): a Response object.

        # Returns
        res (Response or None): an optional response object.
        """

    async def process(self, req: Request, res: Response) -> Response:
        """Process an incoming request.

        - Call `before_dispatch()`. If a response is returned here, no
        further processing is performed.
        - Call the underlying HTTP `app`.
        - Call `after_dispatch()`.
        - Return the response.

        Note: this is aliased to `__call__()`, which means middleware
        instances are callable.

        # Parameters
        req (Request): a Request object.
        res (Response): a Response object.

        # Returns
        res (Response): a Response object.
        """
        before_res = await call_async(self.before_dispatch, req, res)
        if before_res:
            return before_res

        res = await self.app(req, res)

        res = await call_async(self.after_dispatch, req, res) or res

        return res

    __call__ = process
