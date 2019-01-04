from typing import Callable, Awaitable, MutableMapping, Any

from .request import Request
from .response import Response

Scope = dict
Event = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Event]]
Send = Callable[[Event], None]
ASGIAppInstance = Callable[[Receive, Send], Awaitable[None]]
ASGIApp = Callable[[Scope], ASGIAppInstance]
EventHandler = Callable[[], None]
HTTPApp = Callable[[Request, Response], Awaitable[None]]
ErrorHandler = Callable[[Request, Response, Exception], None]
