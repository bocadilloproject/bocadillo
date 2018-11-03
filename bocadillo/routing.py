from typing import AnyStr, Callable

from parse import parse

from .request import Request
from .response import Response


class Route:
    """Represents a route to a view.

    Formatted string syntax is used for route patterns.
    """

    def __init__(self, pattern: AnyStr,
                 handler: Callable[[Request, Response], None]):
        self._pattern = pattern
        self._handler = handler

    def matches(self, path: str) -> bool:
        """Return whether the route matches the given path.

        Examples
        -------
        >>> route = Route('/{age:d}', lambda req, resp: None)
        >>> route.matches('/42')
        True
        >>> route.matches('/john')
        False
        """
        result = parse(self._pattern, path)
        return result is not None

    async def __call__(self, request, response):
        await self._handler(request, response)
