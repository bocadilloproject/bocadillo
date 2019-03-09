from typing import Optional

from .app_types import HTTPApp
from .compat import call_async
from .request import Request
from .response import Response


class Middleware(HTTPApp):
    """Base class for middleware classes.

    # Parameters
    app:
        a callable that may as well be another `Middleware` instance.
    kwargs (any):
        keyword arguments passed when registering the
        middleware on the application.
    """

    def __init__(self, app: HTTPApp, **kwargs):
        self.app = app
        self.kwargs = kwargs

    async def before_dispatch(
        self, req: Request, res: Response
    ) -> Optional[Response]:
        """Perform processing before a request is dispatched.

        If the #::bocadillo.response#Response object is returned,
        it will be used and no further processing will be performed.

        # Parameters
        req: a #::bocadillo.request#Request object.
        res: a #::bocadillo.response#Response object.

        # Returns
        res: an optional #::bocadillo.response#Response object.
        """

    async def after_dispatch(
        self, req: Request, res: Response
    ) -> Optional[Response]:
        """Perform processing after a request has been dispatched.

        # Parameters
        req: a #::bocadillo.request#Request object.
        res: a #::bocadillo.response#Response object.

        # Returns
        res: an optional #::bocadillo.response#Response object.
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
        req: a #::bocadillo.request#Request object.
        res: a #::bocadillo.response#Response object.

        # Returns
        res: a #::bocadillo.response#Response object.
        """
        before_res: Optional[Response] = await call_async(  # type: ignore
            self.before_dispatch, req, res
        )
        if before_res:
            return before_res

        res = await self.app(req, res)

        res = (
            await call_async(self.after_dispatch, req, res)  # type: ignore
            or res
        )

        return res

    __call__ = process
