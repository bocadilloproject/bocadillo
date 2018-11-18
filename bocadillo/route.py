from typing import Optional, List

from parse import parse

from .view import View, create_callable_view


class Route:
    """Represents a route to a view.

    Formatted string syntax is used for route patterns.
    """

    def __init__(self,
                 pattern: str,
                 view: View,
                 methods: List[str],
                 name: str):
        self._pattern = pattern
        self._view = create_callable_view(view=view, methods=methods)
        self._methods = methods
        self._name = name

    def url(self, **kwargs) -> str:
        """Return full path for the given route parameters."""
        return self._pattern.format(**kwargs)

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
        if result is not None:
            return result.named
        return None

    async def __call__(self, request, response, **kwargs) -> None:
        await self._view(request, response, **kwargs)
