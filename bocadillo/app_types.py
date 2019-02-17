from typing import Any, Awaitable, Callable, MutableMapping, Union

from .request import Request
from .response import Response

# ASGI
Scope = dict
Event = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Event]]
Send = Callable[[Event], None]
ASGIAppInstance = Callable[[Receive, Send], Awaitable[None]]
ASGIApp = Callable[[Scope], ASGIAppInstance]

# HTTP
AsyncHandler = Callable[[Request, Response, Any], Awaitable[None]]
SyncHandler = Callable[[Request, Response, Any], None]
Handler = Union[AsyncHandler, SyncHandler]
ErrorHandler = Callable[[Request, Response, Exception], Awaitable[None]]


class HTTPApp:
    async def __call__(self, req: Request, res: Response) -> Response:
        raise NotImplementedError


# Server lifespan events
EventHandler = Callable[[], Awaitable[None]]
