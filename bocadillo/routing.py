import inspect
from functools import partial
from string import Formatter
from typing import Callable, Union, Type, Any
from typing import Optional, TypeVar, Generic, Dict

from parse import parse
from starlette.websockets import WebSocketClose

from . import views
from .app_types import HTTPApp
from .app_types import Scope, Receive, Send
from .errors import HTTPError
from .meta import DocsMeta
from .redirection import Redirection
from .request import Request
from .response import Response
from .views import View, HandlerDoesNotExist
from .websockets import WebSocketView, WebSocket


# Base classes


class BaseRoute:
    # Base route class.

    def __init__(self, pattern: str):
        if not pattern.startswith("/"):
            pattern = f"/{pattern}"
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


# HTTP


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


class RouteDeclarationError(Exception):
    """Raised when a route is ill-declared."""


# WebSocket


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
