import typing

from .request import Request
from .response import Response

if typing.TYPE_CHECKING:  # pragma: no cover
    from .applications import App

# ASGI
Scope = dict
Event = typing.MutableMapping[str, typing.Any]
Receive = typing.Callable[[], typing.Awaitable[Event]]
Send = typing.Callable[[Event], None]


class ASGIApp:
    def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        raise NotImplementedError


# HTTP
Handler = typing.Callable[
    [Request, Response, typing.Any], typing.Awaitable[None]
]
ErrorHandler = typing.Callable[
    [Request, Response, BaseException], typing.Awaitable[None]
]


class HTTPApp:
    async def __call__(self, req: Request, res: Response) -> Response:
        raise NotImplementedError


# Server lifespan events
EventHandler = typing.Callable[[], typing.Awaitable[None]]
