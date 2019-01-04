from typing import Callable, Awaitable

from .request import Request
from .response import Response

HTTPApp = Callable[[Request, Response], Awaitable[None]]
ErrorHandler = Callable[[Request, Response, Exception], None]
