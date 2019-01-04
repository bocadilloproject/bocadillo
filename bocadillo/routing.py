import inspect
from functools import partial
from string import Formatter
from typing import (
    Optional,
    Dict,
    Callable,
    Union,
    Type,
    Any,
    Tuple,
    Generic,
    TypeVar,
)

from parse import parse
from starlette.websockets import WebSocketClose

from bocadillo.app_types import HTTPApp, Receive, Send, Scope
from bocadillo.redirection import Redirection
from . import views
from .http import HTTPError
from .meta import DocsMeta
from .request import Request
from .response import Response
from .views import View, HandlerDoesNotExist
from .websockets import WebSocket, WebSocketView


# Routes


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


class HTTPRoute(BaseRoute, metaclass=DocsMeta):
    """Represents the binding of an URL pattern to an HTTP view.

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

    async def __call__(self, req: Request, res: Response, **params) -> None:
        try:
            await self._view(req, res, **params)
        except HandlerDoesNotExist as e:
            raise HTTPError(405) from e


class WebSocketRoute(BaseRoute, metaclass=DocsMeta):
    """Represents the binding of an URL path to a WebSocket view.

    # Parameters
    pattern (str): an URL pattern.
    view (coroutine function):
        Should take as parameter a `WebSocket` object and
        any extracted route parameters.
    """

    def __init__(self, pattern: str, view: WebSocketView, **kwargs):
        super().__init__(pattern)
        self._view = view
        self._ws_kwargs = kwargs

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send, **params
    ):
        ws = WebSocket(scope, receive, send, **self._ws_kwargs)
        try:
            await self._view(ws, **params)
        except BaseException:
            await ws.ensure_closed(1011)
            raise


R = TypeVar("R", HTTPRoute, WebSocketRoute)


# Routers


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


class HTTPRouter(HTTPApp, BaseRouter[HTTPRoute]):
    # A collection of HTTP routes.

    def add_route(
        self,
        view: Union[View, Type[Any], Callable, Any],
        pattern: str,
        *,
        name: str = None,
        namespace: str = None,
    ) -> HTTPRoute:
        # Build and register a route.

        if isinstance(view, View):
            # View instance. No further conversion required.
            pass
        elif inspect.isclass(view):
            # View-like class.
            view = views.from_obj(view())
        elif callable(view):
            # Function-based view.
            # NOTE: here, we ensure backward-compatibility with the routing of
            # function-based views pre-0.9.
            view = views.from_handler(view)
        else:
            # View-like object.
            view = views.from_obj(view)

        assert isinstance(view, View)

        if name is None:
            name = view.name
        if namespace is not None:
            name = namespace + ":" + name

        check_route(pattern, view)

        route = HTTPRoute(pattern=pattern, view=view, name=name)
        self.routes[name] = route

        return route

    def get_route_or_404(self, name: str) -> HTTPRoute:
        # Return a route or raise a 404 error.
        try:
            return self.routes[name]
        except KeyError as e:
            raise HTTPError(404) from e

    async def __call__(self, req: Request, res: Response) -> Response:
        match = self.match(req.url.path)
        if match is None:
            raise HTTPError(status=404)
        try:
            await match.route(req, res, **match.params)
        except Redirection as redirection:
            res = redirection.response
        return res


class WebSocketRouter(BaseRouter[WebSocketRoute]):
    # A collection of WebSocket routes.

    def add_route(self, pattern: str, view, **kwargs):
        # Register a WebSocket route.
        route = WebSocketRoute(pattern=pattern, view=view, **kwargs)
        self.routes[pattern] = route
        return route

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Dispatch a WebSocket connection request.
        match = self.match(scope["path"])
        if match is None:
            # Close with a 403 error code, as specified in the ASGI spec:
            # https://asgi.readthedocs.io/en/latest/specs/www.html#close
            await WebSocketClose(code=403)(receive, send)
        else:
            await match.route(scope, receive, send, **match.params)


# Mixins


class RoutingMixin:
    """Provide routing capabilities to a class."""

    def __init__(self):
        super().__init__()
        self.http_router = HTTPRouter()
        self.websocket_router = WebSocketRouter()

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
        return self.http_router.route(
            pattern=pattern, name=name, namespace=namespace
        )

    def websocket_route(
        self,
        pattern: str,
        *,
        value_type: Optional[str] = None,
        receive_type: Optional[str] = None,
        send_type: Optional[str] = None,
        caught_close_codes: Optional[Tuple[int]] = None,
    ):
        """Register a WebSocket route by decorating a view.

        # Parameters
        pattern (str): an URL pattern.

        # See Also
        - [WebSocket](./websockets.md#websocket) for a description of keyword
        arguments.
        """
        # NOTE: use named keyword arguments instead of `**kwargs` to improve
        # their accessibility (e.g. for IDE discovery).
        return self.websocket_router.route(
            pattern,
            value_type=value_type,
            receive_type=receive_type,
            send_type=send_type,
            caught_close_codes=caught_close_codes,
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
        route = self.http_router.get_route_or_404(name)
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
    if not pattern.startswith("/"):
        raise RouteDeclarationError(
            f"Route pattern '{pattern}' on view '{view.name}' "
            f"must start with '/' to avoid ambiguities."
        )

    parsed_format = Formatter().parse(pattern)
    route_parameters: set = {name for _, name, _, _ in parsed_format if name}

    for method, handler in views.get_handlers(view).items():
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


class RouteDeclarationError(Exception):
    """Raised when a route is ill-declared."""
