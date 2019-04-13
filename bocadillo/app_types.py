from typing import Any, Awaitable, Callable, MutableMapping, TypeVar

from .request import Request
from .response import Response

_E = TypeVar("_E", bound=Exception)

# ASGI
Scope = dict
Event = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Event]]
Send = Callable[[Event], None]


class ASGIAppInstance:
    def __call__(self, receive: Receive, send: Send) -> None:
        raise NotImplementedError


class ASGIApp:
    def __call__(self, scope: Scope) -> ASGIAppInstance:
        raise NotImplementedError


# HTTP
Handler = Callable[[Request, Response, Any], Awaitable[None]]
ErrorHandler = Callable[[Request, Response, _E], Awaitable[None]]


class HTTPApp:
    async def __call__(self, req: Request, res: Response) -> Response:
        raise NotImplementedError


# Server lifespan events
EventHandler = Callable[[], Awaitable[None]]
