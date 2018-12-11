"""Definition of the Router, a collection of routes."""
import inspect
from functools import partial
from http import HTTPStatus
from typing import Dict, List, Tuple, Optional, NamedTuple

from .checks import check_route
from .route import Route
from ..compat import camel_to_snake
from ..constants import ALL_HTTP_METHODS
from ..exceptions import HTTPError
from ..view import create_async_view, View


class RouteMatch(NamedTuple):
    """Represents the result of a successful route match."""

    route: Route
    params: dict


def _ensure_head_if_get(view: View, methods: List[str]) -> None:
    if inspect.isclass(view):
        if hasattr(view, "get") and not hasattr(view, "head"):
            view.head = view.get
    else:
        if "GET" in methods and "HEAD" not in methods:
            methods.append("HEAD")


class Router:
    """A collection of routes."""

    def __init__(self):
        self._routes: Dict[str, Route] = {}

    def add_route(
        self,
        view: View,
        pattern: str,
        *,
        methods: List[str] = None,
        name: str = None,
        namespace: str = None,
    ):
        """Build and register a route."""
        if methods is None:
            methods = ["get", "head"]

        methods = [method.upper() for method in methods]

        if name is None:
            if inspect.isclass(view):
                name = camel_to_snake(view.__name__)
            else:
                name = view.__name__

        if namespace is not None:
            name = namespace + ":" + name

        _ensure_head_if_get(view, methods)

        if inspect.isclass(view):
            view = view()
            if hasattr(view, "handle"):
                methods = ALL_HTTP_METHODS
            else:
                methods = [
                    method
                    for method in ALL_HTTP_METHODS
                    if method.lower() in dir(view)
                ]

        check_route(pattern, view, methods)
        view = create_async_view(view)

        route = Route(pattern=pattern, view=view, methods=methods, name=name)
        self._routes[name] = route

        return route

    def route_decorator(self, *args, **kwargs):
        """Register a route by decorating a view."""
        return partial(self.add_route, *args, **kwargs)

    def _find_matching_route(self, path: str) -> Tuple[Optional[str], dict]:
        """Find a route matching the given path."""
        for name, route in self._routes.items():
            kwargs = route.parse(path)
            if kwargs is not None:
                return route.pattern, kwargs
        return None, {}

    def match(self, path: str) -> Optional[RouteMatch]:
        for pattern, route in self._routes.items():
            params = route.parse(path)
            if params is not None:
                return RouteMatch(route=route, params=params)
        return None

    def get_route_or_404(self, name: str) -> Route:
        try:
            return self._routes[name]
        except KeyError as e:
            raise HTTPError(HTTPStatus.NOT_FOUND.value) from e
