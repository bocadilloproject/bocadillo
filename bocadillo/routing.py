import inspect
from functools import partial
from http import HTTPStatus
from string import Formatter
from typing import List, Optional, NamedTuple, Dict

from parse import parse

from .compat import camel_to_snake
from .constants import ALL_HTTP_METHODS
from .exceptions import HTTPError, RouteDeclarationError
from .request import Request
from .response import Response
from .views import (
    View,
    get_view_name,
    get_declared_method_views,
    AsyncView,
    create_async_view,
)


class Route:
    """Represents the binding of an URL pattern to a view.

    As a framework user, you will not need to create routes directly. This
    should be done via `@api.route()`.

    # Parameters
    pattern (str): an URL pattern. F-string syntax is supported for parameters.
    view (coroutine function):
        A view given as a coroutine function. Non-async views (synchronous,
        class-based) will have to have been converted beforehand.
    methods (list of str):
        A list of (upper-case) HTTP methods.
    name (str):
        The route's name.
    """

    def __init__(
        self, pattern: str, view: AsyncView, methods: List[str], name: str
    ):
        self._pattern = pattern
        self._view = view
        self._methods = methods
        self._name = name

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

    def raise_for_method(self, req: Request):
        """Fail if the requested method is not supported by the route.

        # Parameters
        req (Request): a `Request` object.

        # Raises
        HTTPError(405): if `req.method` is not one of `methods`.
        """
        if req.method not in self._methods:
            raise HTTPError(status=HTTPStatus.METHOD_NOT_ALLOWED)

    async def __call__(self, req: Request, res: Response, **kwargs) -> None:
        await self._view(req, res, **kwargs)


def check_route(pattern: str, view: View, methods: List[str]) -> None:
    """Check compatibility of a route pattern and a view.

    # Parameters
    pattern (str): an URL pattern.
    view: a function-based or class-based view.
    methods: an upper-cased list of HTTP methods.

    # Raises
    RouteDeclarationError :
        - If one of the `methods` is not a member of `ALL_HTTP_METHODS`.
        - If `pattern` does not have a leading slash.
        - If the `view` does not accept at least two positional arguments
        (for the request and the response objects).
        - If route parameters declared in the pattern do not match those
        used on the view, e.g. a parameter is declared in the pattern, but
        not used in the view or vice-versa.

    # See Also
    - `ALL_HTTP_METHODS` is defined in [constants.py](./constants.md).
    """
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
    ) -> Route:
        """Build and register a route.

        # Parameters
        view: a function-based or class-based view.
        pattern (str): an URL pattern.
        methods (list of str):
            An optional list of HTTP methods.
            Defaults to `["get", "head"]`.
            Ignored for class-based views.
        name (str):
            An optional name for the route.
            If a route already exists for this name, it is replaced.
            Defaults to a snake-cased version of the view's `__name__`.
        namespace (str):
            An optional namespace for the route. If given, it is prefixed
            to the name and separated by a colon, i.e. `{namespace}:{name}`.

        # Returns
        route (Route): the newly registered `Route` object.

        # Raises
        RouteDeclarationError:
            If route validation has failed.

        # See Also
        - [check_route](#check-route) for the route validation algorithm.
        """
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

    def route(self, *args, **kwargs):
        """Register a route by decorating a view.

        # See Also
        - [add_route](#add-route)
        """
        return partial(self.add_route, *args, **kwargs)

    def match(self, path: str) -> Optional[RouteMatch]:
        """Attempt to match an URL path against one of the registered routes.

        # Parameters
        path (str): an URL path.

        # Returns
        match (RouteMatch or None):
            A `RouteMatch` object built from a route that matched against
            `path` and the extracted route parameters, or `None` if none
            matched.
        """
        for pattern, route in self._routes.items():
            params = route.parse(path)
            if params is not None:
                return RouteMatch(route=route, params=params)
        return None

    def get_route_or_404(self, name: str) -> Route:
        """Return a route or raise a 404 error.

        # Parameters
        name (str): a route name.

        # Returns
        route (Route): the `Route` object registered under `name`.

        # Raises
        HTTPError(404): if no route exists for the given `name`.
        """
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

        This is an alias to the underlying router's `route()` decorator.

        # See Also
        - [Router.route](/api/routing.md#route-3)
        """
        return self._router.route(
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
