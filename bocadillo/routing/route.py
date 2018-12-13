from http import HTTPStatus
from typing import Optional, List

from parse import parse

from ..exceptions import HTTPError
from ..view import AsyncView


class Route:
    """Represents a route to a view.

    Formatted string syntax is used for route patterns.
    """

    def __init__(
        self, pattern: str, view: AsyncView, methods: List[str], name: str
    ):
        self._pattern = pattern
        self._view = view
        self._methods = methods
        self._name = name

    @property
    def pattern(self) -> str:
        return self._pattern

    def url(self, **kwargs) -> str:
        """Return full path for the given route parameters."""
        return self._pattern.format(**kwargs)

    def parse(self, path: str) -> Optional[dict]:
        """Parse an URL path against the route's URL pattern.

        # Returns

        result (dict or None):
            If the URL path matches the URL pattern, this is a dictionary
            containing the route parameters, otherwise None.

        # Examples

        >>> route = Route("/{age:d}", lambda req, res: None)
        >>> route.parse("/42")
        {"age": 42}
        >>> route.parse("/john")
        None
        """
        result = parse(self._pattern, path)
        if result is not None:
            return result.named
        return None

    def raise_for_method(self, request):
        if request.method not in self._methods:
            raise HTTPError(status=HTTPStatus.METHOD_NOT_ALLOWED)

    async def __call__(self, request, response, **kwargs) -> None:
        await self._view(request, response, **kwargs)
