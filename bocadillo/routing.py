import inspect
from functools import partial
from typing import Callable, Union, Type, Any
from typing import Optional, TypeVar, Generic, Dict

from parse import parse
from starlette.websockets import WebSocketClose

from . import views
from .app_types import HTTPApp
from .app_types import Scope, Receive, Send
from .errors import HTTPError
from .redirection import Redirection
from .request import Request
from .response import Response
from .views import View, HandlerDoesNotExist
from .websockets import WebSocketView, WebSocket


# Base classes


class BaseRoute:
    """The base route class.

    # Parameters
    pattern (str): an URL pattern.
    """

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


_R = TypeVar("_R")


class RouteMatch(Generic[_R]):
    """Represents a match between an URL path and a route.

    # Parameters
    route (BaseRoute): a route object.
    params (dict): extracted route parameters.
    """

    def __init__(self, route: _R, params: dict):
        self.route = route
        self.params = params


class BaseRouter(Generic[_R]):
    """The base router class.

    # Attributes
    routes (dict):
        A mapping of patterns to route objects.
    """

    def __init__(self):
        self.routes: Dict[str, _R] = {}

    def add_route(self, *args, **kwargs):
        """Register a route. Not implemented."""
        raise NotImplementedError

    def route(self, *args, **kwargs):
        """Register a route by decorating a view."""
        return partial(self.add_route, *args, **kwargs)

    def match(self, path: str) -> Optional[RouteMatch[_R]]:
        """Attempt to match an URL path against one of the registered routes.

        # Parameters
        path (str): an URL path

        # Returns
        match (RouteMatch or None):
            a `RouteMatch` object if the path matched a registered route,
            `None` otherwise.
        """
        for route in self.routes.values():
            params = route.parse(path)
            if params is not None:
                return RouteMatch(route=route, params=params)
        return None


# HTTP


class HTTPRoute(BaseRoute):
    """Represents the binding of an URL pattern to an HTTP view.

    # Parameters
    pattern (str): an URL pattern.
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
    """A router for HTTP routes.

    Extends [BaseRouter](#baserouter).

    Note: routes are stored by `name` instead of `pattern`.
    """

    def add_route(
        self,
        view: Union[View, Type[Any], Callable, Any],
        pattern: str,
        *,
        name: str = None,
        namespace: str = None,
    ) -> HTTPRoute:
        """Register an HTTP route.

        If the given `view` is not a `View` object, it is converted to one:

        - Classes are instanciated (without arguments) and converted with
        [from_obj].
        - Callables are converted with [from_handler].
        - Any other object is interpreted as a view-like object, and converted
        with [from_obj].

        [from_handler]: /api/views.md#from-handler
        [from_obj]: /api/views.md#from-obj

        # Parameters
        view (View, class, callable, or object):
            convertible to `View` (see above).
        pattern (str): an URL pattern.
        name (str): a route name (inferred from the view if not given).
        namespace (str): an optional route namespace.

        # Returns
        route (HTTPRoute): the registered route.
        """
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

    async def __call__(self, req: Request, res: Response) -> Response:
        match = self.match(req.url.path)
        if match is None:
            raise HTTPError(status=404)
        try:
            await match.route(req, res, **match.params)
        except Redirection as redirection:
            res = redirection.response
        return res


# WebSocket


class WebSocketRoute(BaseRoute):
    """Represents the binding of an URL path to a WebSocket view.

    [WebSocket]: /api/websockets.md#websocket

    # Parameters
    pattern (str): an URL pattern.
    view (coroutine function):
        Should take as parameter a `WebSocket` object and
        any extracted route parameters.
    kwargs (any): passed when building the [WebSocket] object.
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
    """A router for WebSocket routes.

    Extends [BaseRouter](#baserouter).
    """

    def add_route(self, pattern: str, view: WebSocketView, **kwargs):
        """Register a WebSocket route.

        # Parameters
        pattern (str): an URL pattern.
        view (coroutine function): a WebSocket view.

        # Returns
        route (WebSocketRoute): the registered route.
        """
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
