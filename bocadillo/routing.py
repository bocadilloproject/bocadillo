import inspect
from functools import partial
from http import HTTPStatus
from string import Formatter
from typing import List, Optional, NamedTuple, Dict

from parse import parse

from .compat import camel_to_snake
from .constants import ALL_HTTP_METHODS
from .exceptions import HTTPError, RouteDeclarationError
from .views import (
    View,
    get_view_name,
    get_declared_method_views,
    AsyncView,
    create_async_view,
)


def check_route(pattern: str, view: View, methods: List[str]) -> None:
    """Check compatibility of a route pattern and a view."""
    view_name = get_view_name(view)

    for method in methods:
        if method not in ALL_HTTP_METHODS:
            raise RouteDeclarationError(
                f"Route '{view_name}' accepts method '{method}' "
                "but it is not one of the valid HTTP methods: "
                f"{', '.join(ALL_HTTP_METHODS)}"
            )

    if not pattern.startswith("/"):
        raise RouteDeclarationError(
            f"Route pattern '{pattern}' on view '{view_name}' "
            f"must start with '/' to avoid ambiguities."
        )

    _check_route_parameters(pattern, view)


def _check_route_parameters(pattern: str, view: View, _base=None) -> None:
    """Verify that a view accepts parameters defined in a route pattern.

    # Raises
    RouteDeclarationError :
        If a route parameter is not one of the view's arguments,
        of a view argument was not declared in the route pattern.
    """

    parsed_format = Formatter().parse(pattern)
    route_parameters: set = {name for _, name, _, _ in parsed_format if name}

    if callable(view):
        view_name = get_view_name(view=view, base=_base)
        view_parameters = dict(inspect.signature(view).parameters)

        # Necessary if view is from a class-based view.
        view_parameters.pop("self", None)

        for route_param in route_parameters:
            if route_param not in view_parameters:
                raise RouteDeclarationError(
                    f"Parameter '{route_param}' was declared on route "
                    f"'{view_name}()' and should be one of "
                    "its arguments."
                )

        if len(view_parameters) < 2:
            raise RouteDeclarationError(
                f"View '{view_name}' must have at least two "
                "parameters (request and response)."
            )

        for i, view_param in enumerate(view_parameters):
            is_req_or_res = i < 2
            if is_req_or_res:
                continue
            if view_param not in route_parameters:
                raise RouteDeclarationError(
                    f"Parameter '{view_param}' is expected by route "
                    f"'{view_name}' but was not declared in the "
                    "route pattern."
                )
    else:
        for method, method_view in get_declared_method_views(view):
            _check_route_parameters(pattern, method_view, _base=view)


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


class RouteMatch(NamedTuple):
    """Represents the result of a successful route match."""

    route: Route
    params: dict


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


class RoutingMixin:
    """Provide routing capabilities to a class."""

    def __init__(self):
        super().__init__()
        self._router = Router()

    def route(
        self,
        pattern: str,
        *,
        methods: List[str] = None,
        name: str = None,
        namespace: str = None,
    ):
        """Register a new route by decorating a view.

        # Parameters
        pattern (str):
            An URL pattern given as a format string.
        methods (list of str):
            HTTP methods supported by this route.
            Defaults to all HTTP methods.
            Ignored for class-based views.
        name (str):
            A name for this route, which must be unique. Defaults to
            a name based on the view.
        namespace (str):
            A namespace for this route (optional).
            If given, will be prefixed to the `name` and separated by a colon,
            e.g. `"blog:index"`.

        # Raises
        RouteDeclarationError:
            If any method is not a valid HTTP method,
            if `pattern` defines a parameter that the view does not accept,
            if the view uses a parameter not defined in `pattern`,
            if the `pattern` does not start with `/`,
            or if the view did not accept the `req` and `res` parameters.

        # Example
        ```python
        >>> import bocadillo
        >>> api = bocadillo.API()
        >>> @api.route("/greet/{person}")
        ... def greet(req, res, person: str):
        ...     pass
        ```
        """
        return self._router.route_decorator(
            pattern=pattern, methods=methods, name=name, namespace=namespace
        )

    def url_for(self, name: str, **kwargs) -> str:
        """Build the URL path for a named route.

        # Parameters
        name (str): the name of the route.
        kwargs (dict): route parameters.

        # Returns
        url (str): the URL path for a route.

        # Raises
        HTTPError(404) : if no route exists for the given `name`.
        """
        route = self._router.get_route_or_404(name)
        return route.url(**kwargs)


def _ensure_head_if_get(view: View, methods: List[str]) -> None:
    if inspect.isclass(view):
        if hasattr(view, "get") and not hasattr(view, "head"):
            view.head = view.get
    else:
        if "GET" in methods and "HEAD" not in methods:
            methods.append("HEAD")
