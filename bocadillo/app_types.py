from typing import Callable, Awaitable, MutableMapping, Any

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
HTTPApp = Callable[[Request, Response], Awaitable[None]]
ErrorHandler = Callable[[Request, Response, Exception], None]
