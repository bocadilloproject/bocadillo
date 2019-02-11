import inspect
from functools import partial
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from parse import Parser
from starlette.websockets import WebSocketClose

from . import views
from .app_types import HTTPApp, Receive, Scope, Send
from .errors import HTTPError
from .redirection import Redirection
from .request import Request
from .response import Response
from .views import HandlerDoesNotExist, View
from .websockets import WebSocket, WebSocketView

WILDCARD = "{}"

_T = TypeVar("_T")

# Base classes


class BaseRoute:
    """The base route class.

    # Parameters
    pattern (str): an URL pattern.
    """

    def __init__(self, pattern: str):
        if pattern != WILDCARD and not pattern.startswith("/"):
            pattern = f"/{pattern}"
        self._pattern = pattern
        self._parser = Parser(self._pattern)

    @property
    def pattern(self) -> str:
        return self._pattern

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
        params (dict or None):
            If the URL path matches the URL pattern, this is a dictionary
            containing the route parameters, otherwise it is `None`.
        """
        result = self._parser.parse(path)
        return result.named if result is not None else None

    def _get_clone_kwargs(self) -> dict:
        return {"pattern": self._pattern}

    def clone(self, **kwargs: Any):
        kwargs = {**self._get_clone_kwargs(), **kwargs}
        return type(self)(**kwargs)

    async def __call__(self, *args, **kwargs):
        raise NotImplementedError


class RouteMatch(Generic[_T]):  # pylint: disable=unsubscriptable-object
    """Represents a match between an URL path and a route.

    # Parameters
    route (BaseRoute): a route object.
    params (dict): extracted route parameters.
    """

    def __init__(self, route: _T, params: dict):
        self.route = route
        self.params = params


class BaseRouter(Generic[_T]):
    """The base router class.

    # Attributes
    routes (dict):
        A mapping of patterns to route objects.
    """

    def __init__(self):
        self.routes: Dict[str, _T] = {}

    def _get_key(self, route: _T) -> str:
        raise NotImplementedError

    def add_route(self, *args, **kwargs):
        """Register a route. Not implemented."""
        raise NotImplementedError

    def add(self, route: _T):
        self.routes[self._get_key(route)] = route

    def route(self, *args, **kwargs):
        """Register a route by decorating a view."""
        return partial(self.add_route, *args, **kwargs)

    def match(self, path: str) -> Optional[RouteMatch[_T]]:
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

    def mount(self, other: "BaseRouter[_T]", root: str = ""):
        for route in other.routes.values():
            self.add(route.clone(pattern=root + route.pattern))


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
        self.view = view
        self.name = name

    def _get_clone_kwargs(self) -> dict:
        kwargs = super()._get_clone_kwargs()
        kwargs.update({"view": self.view, "name": self.name})
        return kwargs

    async def __call__(self, req: Request, res: Response, **params):
        method = req.method.lower()

        try:
            handler = self.view.get_handler(method)
        except HandlerDoesNotExist as e:
            raise HTTPError(405) from e

        await handler(req, res, **params)


class HTTPRouter(HTTPApp, BaseRouter[HTTPRoute]):
    """A router for HTTP routes.

    Extends [BaseRouter](#baserouter).

    Note: routes are stored by `name` instead of `pattern`.
    """

    def _get_key(self, route: HTTPRoute) -> str:
        return route.name

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
        self.add(route)

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
        self.view = view
        self._ws_kwargs = kwargs

    def _get_clone_kwargs(self) -> dict:
        kwargs = super()._get_clone_kwargs()
        kwargs.update({"view": self.view, **self._ws_kwargs})
        return kwargs

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send, **params
    ):
        ws = WebSocket(scope, receive=receive, send=send, **self._ws_kwargs)
        try:
            await self.view(ws, **params)
        except BaseException:
            await ws.ensure_closed(1011)
            raise


class WebSocketRouter(BaseRouter[WebSocketRoute]):
    """A router for WebSocket routes.

    Extends [BaseRouter](#baserouter).
    """

    def _get_key(self, route: WebSocketRoute) -> str:
        return route.pattern

    def add_route(self, view: WebSocketView, pattern: str, **kwargs):
        """Register a WebSocket route.

        # Parameters
        pattern (str): an URL pattern.
        view (coroutine function): a WebSocket view.

        # Returns
        route (WebSocketRoute): the registered route.
        """
        route = WebSocketRoute(pattern=pattern, view=view, **kwargs)
        self.add(route)
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


class RoutingMixin:
    """Provide HTTP and WebSocket routing to an application class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
            pattern=pattern,
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
        route = self.http_router.routes.get(name)
        if route is None:
            raise HTTPError(404)
        return route.url(**kwargs)

    def redirect(
        self,
        *,
        name: str = None,
        url: str = None,
        permanent: bool = False,
        **kwargs,
    ):
        """Redirect to another HTTP route.

        # Parameters
        name (str): name of the route to redirect to.
        url (str):
            URL of the route to redirect to (required if `name` is omitted).
        permanent (bool):
            If `False` (the default), returns a temporary redirection (302).
            If `True`, returns a permanent redirection (301).
        kwargs (dict):
            Route parameters.

        # Raises
        Redirection:
            an exception that will be caught to trigger a redirection.

        # See Also
        - [Redirecting](../guides/http/redirecting.md)
        """
        if name is not None:
            url = self.url_for(name=name, **kwargs)
        else:
            assert url is not None, "url is expected if no route name is given"
        raise Redirection(url=url, permanent=permanent)
