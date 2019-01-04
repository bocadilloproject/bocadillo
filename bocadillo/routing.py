from functools import partial
from typing import Optional, TypeVar, Generic, Dict

from parse import parse


class BaseRoute:
    # Base route class.

    def __init__(self, pattern: str):
        self._pattern = pattern

    def url(self, **kwargs) -> str:
        """Return full path for the given route parameters.

        # Parameters
        kwargs (dict): route parameters.

        # Returns
        url (str):
            A full URL path obtained by formatting the route pattern with
            the provided route parameters.
        """
        return self._pattern.format(**kwargs)

    def parse(self, path: str) -> Optional[dict]:
        """Parse an URL path against the route's URL pattern.

        # Returns
        result (dict or None):
            If the URL path matches the URL pattern, this is a dictionary
            containing the route parameters, otherwise None.
        """
        result = parse(self._pattern, path)
        if result is not None:
            return result.named
        return None

    async def __call__(self, *args, **kwargs):
        raise NotImplementedError


R = TypeVar("R")


class RouteMatch(Generic[R]):
    # Represents a match between an URL path and a route.

    def __init__(self, route: R, params: dict):
        self.route = route
        self.params = params


class BaseRouter(Generic[R]):
    # A collection of routes.

    def __init__(self):
        self.routes: Dict[str, R] = {}

    def add_route(self, *args, **kwargs):
        raise NotImplementedError

    def route(self, *args, **kwargs):
        # Register a route by decorating a view.
        return partial(self.add_route, *args, **kwargs)

    def match(self, path: str) -> Optional[RouteMatch[R]]:
        # Attempt to match an URL path against one of the registered routes.
        for route in self.routes.values():
            params = route.parse(path)
            if params is not None:
                return RouteMatch(route=route, params=params)
        return None
