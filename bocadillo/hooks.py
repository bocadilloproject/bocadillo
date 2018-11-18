from typing import Callable

from .request import Request
from .response import Response
from .view import View

HookFunction = Callable[[Request, Response, View, dict], None]
