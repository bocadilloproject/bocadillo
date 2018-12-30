import inspect
from functools import partial
from string import Formatter
from typing import Optional, NamedTuple, Dict, Callable, Union, Type, Any

from parse import parse

from .compat import camel_to_snake
from .exceptions import HTTPError, RouteDeclarationError
from .meta import DocsMeta
from .request import Request
from .response import Response
from .views import View, Handler, get_handlers, view as view_decorator


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


class Route(BaseRoute, metaclass=DocsMeta):
    """Represents the binding of an URL pattern to a view.

    Note: as a framework user, you will not need to create routes directly.

    # Parameters
    pattern (str): an URL pattern. F-string syntax is supported for parameters.
    view (View):
        A `View` object.
    name (str):
        The route's name.
    """

    def __init__(self, pattern: str, view: View, name: str):
        super().__init__(pattern)
        self._view = view
        self._name = name

    async def __call__(self, req: Request, res: Response, **kwargs) -> None:
        try:
            handler: Handler = getattr(self._view, req.method.lower())
        except AttributeError as e:
            print(e)
            raise HTTPError(405) from e
        else:
            await handler(req, res, **kwargs)


class RouteMatch(NamedTuple):
    # Represents the result of a successful route match.

    route: Route
    params: dict


class Router:
    # A collection of routes.

    def __init__(self):
        self._routes: Dict[str, Route] = {}

    def add_route(
        self,
        view: Union[View, Type[Any], Callable, Any],
        pattern: str,
        *,
        name: str = None,
        namespace: str = None,
    ) -> Route:
        # Build and register a route.
        if isinstance(view, View):
            # View instance. No further conversion required.
            pass
        # Otherwise, convert the view to a View instance and recurse.
        elif inspect.isclass(view):
            # View-like class.
            view = View.from_obj(view())
            return self.add_route(view, pattern, name=name, namespace=namespace)
        elif callable(view):
            # Function-based view.
            # NOTE: here, we ensure backward-compatibility with the routing of
            # function-based views pre-0.9.
            view = view_decorator()(view)
            return self.add_route(view, pattern, name=name, namespace=namespace)
        else:
            # View-like object.
            view = View.from_obj(view)
            return self.add_route(view, pattern, name=name, namespace=namespace)

        # `view` is now a proper `View` object.

        if name is None:
            name = camel_to_snake(view.__name__)
        if namespace is not None:
            name = namespace + ":" + name

        check_route(pattern, view)

        route = Route(pattern=pattern, view=view, name=name)
        self._routes[name] = route

        return route

    def route(self, *args, **kwargs):
        # Register a route by decorating a view.
        return partial(self.add_route, *args, **kwargs)

    def match(self, path: str) -> Optional[RouteMatch]:
        # Attempt to match an URL path against one of the registered routes.
        # NOTE: websocket (bool) = whether to look for an HTTP (`False`)
        # or WebSocket (`True`) route.
        for pattern, route in self._routes.items():
            params = route.parse(path)
            if params is not None:
                return RouteMatch(route=route, params=params)
        return None

    def get_route_or_404(self, name: str) -> Route:
        # Return a route or raise a 404 error.
        try:
            return self._routes[name]
        except KeyError as e:
            raise HTTPError(404) from e


class RoutingMixin:
    """Provide routing capabilities to a class."""

    def __init__(self):
        super().__init__()
        self._router = Router()

    def route(self, pattern: str, *, name: str = None, namespace: str = None):
        """Register a new route by decorating a view.

        # Parameters
        pattern (str): an URL pattern.
        methods (list of str):
            An optional list of HTTP methods.
            Defaults to `["get", "head"]`.
            Ignored for class-based views.
        name (str):
            An optional name for the route.
            If a route already exists for this name, it is replaced.
            Defaults to a snake-cased version of the view's name.
        namespace (str):
            An optional namespace for the route. If given, it is prefixed to
            the name and separated by a colon.

        # Raises
        RouteDeclarationError:
            If route validation has failed.

        # See Also
        - [check_route](#check-route) for the route validation algorithm.
        """
        return self._router.route(
            pattern=pattern, name=name, namespace=namespace
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


def check_route(pattern: str, view: View) -> None:
    """Check compatibility of a route pattern and a view.

    # Parameters
    pattern (str): an URL pattern.
    view (View): a `View` object.

    # Raises
    RouteDeclarationError :
        - If `pattern` does not have a leading slash.
        - If route parameters declared in the pattern do not match those
        of any view handler, e.g. a parameter is declared in the pattern, but
        not used in the handler or vice-versa.

    # See Also
    - `ALL_HTTP_METHODS` is defined in [constants.py](./constants.md).
    """
    view_name = view.__class__.__name__

    if not pattern.startswith("/"):
        raise RouteDeclarationError(
            f"Route pattern '{pattern}' on view '{view_name}' "
            f"must start with '/' to avoid ambiguities."
        )

    parsed_format = Formatter().parse(pattern)
    route_parameters: set = {name for _, name, _, _ in parsed_format if name}

    for method, handler in get_handlers(view).items():
        handler_parameters = dict(inspect.signature(handler).parameters)
        handler_parameters.pop("self", None)  # paranoia check
        handler_parameters = list(handler_parameters)

        for route_param in route_parameters:
            if route_param not in handler_parameters:
                raise RouteDeclarationError(
                    f"Route pattern '{pattern}' declares the route parameter "
                    f"'{route_param}' and should be a parameter of "
                    f"'{handler.__qualname__}'."
                )

        for handler_param in handler_parameters[2:]:
            if handler_param not in route_parameters:
                raise RouteDeclarationError(
                    f"Handler '{handler.__qualname__}' expects parameter "
                    f"'{handler_param}' but it was not declared in the route "
                    f"pattern '{pattern}'"
                )
