from typing import AnyStr, Callable, Optional

from parse import parse

from .request import Request
from .response import Response


class Route:
    """Represents a route to a view.

    Formatted string syntax is used for route patterns.
    """

    def __init__(self, pattern: AnyStr,
                 handler: Callable[[Request, Response, dict], None]):
        self._pattern = pattern
        self._handler = handler

    def match(self, path: str) -> Optional[dict]:
        """Return whether the route matches the given path.

        Examples
        -------
        >>> route = Route('/{age:d}', lambda req, resp: None)
        >>> route.match('/42')
        {'age': 42}
        >>> route.match('/john')
        None
        """
        result = parse(self._pattern, path)
        return result is not None and result.named or None

    async def __call__(self, request, response, **kwargs):
        await self._handler(request, response, **kwargs)
