from typing import Callable, Optional

from .request import Request
from .response import Response

HookFunction = Callable[[Request, Response, Optional[dict]], None]

BEFORE = 'before'
AFTER = 'after'


def empty_hook(req, res, params):
    pass
