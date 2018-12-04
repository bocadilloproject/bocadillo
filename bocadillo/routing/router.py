"""Definition of the Router, a collection of routes."""
import inspect
from functools import partial
from http import HTTPStatus
from typing import Dict, List, Tuple, Optional, NamedTuple

from .checks import check_route
from .route import Route
from ..constants import ALL_HTTP_METHODS
from ..exceptions import HTTPError
from ..view import create_async_view, AsyncView


class RouteMatch(NamedTuple):
    """Represents the result of a successful route match."""

    route: Route
    params: dict


class Router:
    """A collection of routes."""

    def __init__(self):
        self._routes: Dict[str, Route] = {}
        self._named_routes: Dict[str, Route] = {}

    def mount(self, prefix: str, other: 'Router'):
        """Mount another router at the given prefix.

        In practice, copy routes and named routes by adding `prefix` to
        each route's pattern.
        """
        for pattern, route in other._routes.items():
            self._register_from(route, pattern=prefix + pattern)
        for name, route in other._named_routes.items():
            pattern = prefix + route.pattern
            self._register_from(route, pattern=pattern, name=name)

    def _register_from(self, route, **kwargs):
        kwargs.setdefault('pattern', route.pattern)
        kwargs.setdefault('view', route.view)
        kwargs.setdefault('methods', route.methods)
        return self._register(**kwargs)

    def _register(
        self,
        pattern: str,
        view: AsyncView,
        methods: List[str],
        name: str = None,
    ):
        route = Route(pattern=pattern, view=view, methods=methods, name=name)
        self._routes[pattern] = route
        if name is not None:
            self._named_routes[name] = route
        return route

    def add_route(
        self, view, pattern: str, *, methods: List[str] = None, name: str = None
    ):
        """Register a route."""
        if inspect.isclass(view):
            view = view()
            if hasattr(view, 'handle'):
                methods = ALL_HTTP_METHODS
            else:
                methods = [
                    method
                    for method in ALL_HTTP_METHODS
                    if method.lower() in dir(view)
                ]

        check_route(pattern, view, methods)

        view = create_async_view(view)

        return self._register(
            pattern=pattern, view=view, methods=methods, name=name
        )

    def route_decorator(
        self, pattern: str, *, methods: List[str] = None, name: str = None
    ):
        """Register a route by decorating a view."""
        if methods is None:
            methods = ALL_HTTP_METHODS

        methods = [method.upper() for method in methods]

        return partial(
            self.add_route, pattern=pattern, methods=methods, name=name
        )

    def get(self, pattern: str) -> Optional[Route]:
        return self._routes.get(pattern)

    def _find_matching_route(self, path: str) -> Tuple[Optional[str], dict]:
        """Find a route matching the given path."""
        for pattern, route in self._routes.items():
            kwargs = route.parse(path)
            if kwargs is not None:
                return pattern, kwargs
        return None, {}

    def match(self, path: str) -> Optional[RouteMatch]:
        for pattern, route in self._routes.items():
            params = route.parse(path)
            if params is not None:
                return RouteMatch(route=route, params=params)
        return None

    def get_route_or_404(self, name: str):
        try:
            return self._named_routes[name]
        except KeyError as e:
            raise HTTPError(HTTPStatus.NOT_FOUND.value) from e
