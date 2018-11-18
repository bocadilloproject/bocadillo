from typing import Callable

from .request import Request
from .response import Response
from .view import View

HookFunction = Callable[[Request, Response, View, dict], None]

BEFORE = 'before'
AFTER = 'after'


def empty_hook(req, res, view, params):
    pass
