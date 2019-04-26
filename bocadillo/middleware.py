import typing

from .app_types import HTTPApp
from .compat import check_async
from .request import Request
from .response import Response

if typing.TYPE_CHECKING:  # pragma: no cover
    from .applications import App


class MiddlewareMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        for callback in "before_dispatch", "after_dispatch":
            check_async(
                getattr(cls, callback),
                reason="'{name}.{callback}' must be asynchronous",
            )
        return cls


class Middleware(HTTPApp, metaclass=MiddlewareMeta):
    """Base class for middleware classes.

    # Parameters
    inner (callable): the inner middleware that this middleware wraps.
    """

    def __init__(self, inner: HTTPApp):
        self.inner = inner

    async def before_dispatch(
        self, req: Request, res: Response
    ) -> typing.Optional[Response]:
        """Perform processing before a request is dispatched.

        If the #::bocadillo.response#Response object is returned,
        it will be used and no further processing will be performed.

        # Parameters
        req: a #::bocadillo.request#Request object.
        res: a #::bocadillo.response#Response object.

        # Returns
        res: an optional #::bocadillo.response#Response object.
        """

    async def after_dispatch(self, req: Request, res: Response) -> None:
        """Perform processing after a request has been dispatched.

        # Parameters
        req: a #::bocadillo.request#Request object.
        res: a #::bocadillo.response#Response object.
        """

    async def __call__(self, req: Request, res: Response) -> Response:
        before_res = await self.before_dispatch(req, res)

        if before_res is not None:
            return before_res

        res = await self.inner(req, res)

        await self.after_dispatch(req, res)

        return res
