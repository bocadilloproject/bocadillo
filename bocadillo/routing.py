"""This module defines classes (both abstract and concrete) that power routing.

**Notations**: this modules uses the following [generic types]:

- `_R` refers to a route object, i.e. an instance of a subclass of [BaseRoute](#baseroute).
- `_V` refers to a view object.

[generic types]: https://docs.python.org/3/library/typing.html#generics
"""

import inspect
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    NoReturn,
    Optional,
    Tuple,
    Type,
    TypeVar,
)

from starlette.websockets import WebSocketClose

from . import views
from .app_types import HTTPApp, Receive, Scope, Send
from .errors import HTTPError
from .injection import consumer
from .redirection import Redirection
from .request import Request
from .response import Response
from .urlparse import Parser
from .views import AsyncHandler, HandlerDoesNotExist, View
from .websockets import WebSocket, WebSocketView

# Route generic types.
_R = TypeVar("_R", bound="BaseRoute")  # route
_V = TypeVar("_V")  # view


# Utilities.


class RouteMatch(Generic[_R]):  # pylint: disable=unsubscriptable-object
    """Represents a match between an URL path and a route.

    # Parameters
    route: a route object (subclass of #::bocadillo.routing#BaseRoute).
    params (dict): extracted route parameters.
    """

    __slots__ = ("route", "params")

    def __init__(self, route: _R, params: dict):
        self.route = route
        self.params = params


# Base classes.


class BaseRoute(Generic[_V]):
    """The base route class.

    This is referenced as `_R` in the rest of this module.

    # Parameters
    pattern (str): an URL pattern.
    view (_V):
        a view function or object whose actual type is defined by concrete
        routes.
    """

    __slots__ = ("_pattern", "_parser", "view")

    def __init__(self, pattern: str, view: _V):
        self._parser = Parser(pattern)
        self.view = view

    @property
    def pattern(self) -> str:
        return self._parser.pattern

    def url(self, **kwargs) -> str:
        """Return the full URL path for the given route parameters.

        # Parameters
        kwargs (dict): route parameters.

        # Returns
        url (str):
            A full URL path obtained by formatting the route pattern with
            the provided route parameters.
        """
        return self.pattern.format(**kwargs)

    def parse(self, path: str) -> Optional[dict]:
        """Parse an URL path against the route's URL pattern.

        # Returns
        params (dict or None):
            If the URL path matches the URL pattern, this is a dictionary
            containing the route parameters, otherwise it is `None`.
        """
        return self._parser.parse(path)

    @classmethod
    def normalize(cls, view: Any) -> _V:
        """Perform any conversion necessary to return a proper view object.

        Not implemented.
        """
        raise NotImplementedError

    @classmethod
    def build(cls, view: _V, pattern: str, **kwargs) -> _R:
        """Create a route out of a normalized view."""
        return cls(view=view, pattern=pattern, **kwargs)

    @classmethod
    def create(cls, view: Any, pattern: str, **kwargs) -> _R:
        """Normalize a view and build and a route instance."""
        view: _V = cls.normalize(view)
        return cls.build(view, pattern=pattern, **kwargs)


class BaseRouter(Generic[_R, _V]):
    """The base router class.

    # Attributes
    routes (dict):
        a mapping of URL patterns to route objects.
    """

    __slots__ = ("routes", "route_class")

    route_class: Type[_R]

    def __init__(self):
        self.routes: Dict[str, _R] = {}

    def _get_key(self, route: _R) -> str:
        # Return the key at which `route` should be stored internally.
        raise NotImplementedError

    def add_route(self, route: _R) -> None:
        """Register a route."""
        self.routes[self._get_key(route)] = route

    def route(self, *args, **kwargs) -> Callable[[Any], _R]:
        """Register a route by decorating a view.

        The decorated function or class will be converted to a proper view using
        [`.normalize()`](#normalize), and then fed to
        [`.add_route()`](#add-route).

        # Parameters
        *args, **kwargs:
            passed to [`.add_route()`](#add-route)
            along with the normalized view.
        """

        def decorate(view: Any) -> _R:
            route = self.route_class.create(view, *args, **kwargs)
            self.add_route(route)

        return decorate

    def match(self, path: str) -> Optional[RouteMatch[_R]]:
        """Attempt to match an URL path against one of the registered routes.

        # Parameters
        path (str): an URL path

        # Returns
        match:
            a #::bocadillo.routing#RouteMatch object if the path matched
            a registered route, `None` otherwise.
        """
        for route in self.routes.values():
            params = route.parse(path)
            if params is not None:
                return RouteMatch(route=route, params=params)
        return None


# HTTP.


class HTTPRoute(BaseRoute[View]):
    """Represents the binding of an URL pattern to an HTTP view.

    Subclass of #::bocadillo.routing#BaseRoute.

    # Parameters
    pattern (str):
        an URL pattern.
    view:
        a #::bocadillo.views#View object.
    name (str):
        the route's name.
    """

    __slots__ = ("name",)

    def __init__(self, pattern: str, view: View, name: str):
        super().__init__(pattern, view)
        self.name = name

    @classmethod
    def normalize(cls, view: Any) -> View:
        """Build a #::bocadillo.views#View object.

        The input, free-form `view` object is converted using the following
        rules:

        - Classes are instanciated (without arguments) and converted with
        [`from_obj()`][obj].
        - Callables are converted with [`from_handler()`][handler].
        - Any other object is interpreted as a view-like object, and converted
        with [`from_obj()`][obj].

        [obj]: ./views.md#from-obj
        [handler]: ./views.md#from-handler

        # Returns
        view:
            a #::bocadillo.views#View object,
            ready to be fed to [`.add_route()`](#add-route).
        """
        if isinstance(view, View):
            return view

        if inspect.isclass(view):
            # View-like class.
            return views.from_obj(view())

        if callable(view):
            # Function-based view.
            # NOTE: here, we ensure backward-compatibility with the routing of
            # function-based views pre-0.9.
            return views.from_handler(view)

        # Treat as a view-like object.
        return views.from_obj(view)

    @classmethod
    def build(
        cls,
        view: View,
        pattern: str,
        name: str = None,
        namespace: str = None,
        **kwargs,
    ) -> "HTTPRoute":
        """Build an HTTP route.

        # Parameters
        view:
            a #::bocadillo.views#View object
            obtained via [.normalize()](#normalize-2).
        pattern (str): an URL pattern.
        name (str): a route name (inferred from the view if not given).
        namespace (str): an optional route namespace.

        # Returns
        route: an instance of #::bocadillo.routing#HTTPRoute.
        """
        if name is None:
            name = view.name
        if namespace is not None:
            name = namespace + ":" + name

        return super().build(view=view, pattern=pattern, name=name)

    async def __call__(self, req: Request, res: Response, **params):
        method: str = req.method.lower()

        try:
            handler: AsyncHandler = self.view.get_handler(method)
        except HandlerDoesNotExist as e:
            raise HTTPError(405) from e

        await handler(req, res, **params)  # type: ignore


class HTTPRouter(HTTPApp, BaseRouter[HTTPRoute, View]):
    """A router for HTTP routes.

    Subclass of #::bocadillo.routing#BaseRouter.

    Note: routes are stored by `name` instead of `pattern`.
    """

    route_class = HTTPRoute

    def _get_key(self, route: HTTPRoute) -> str:
        # NOTE: this ensures that no two routes stored in this
        # router have the same name.
        return route.name

    async def __call__(self, req: Request, res: Response) -> Response:
        match = self.match(req.url.path)

        if match is None:
            raise HTTPError(status=404)

        try:
            await match.route(req, res, **match.params)
        except Redirection as redirection:
            res = redirection.response

        return res


# WebSocket.


class WebSocketRoute(BaseRoute[WebSocketView]):
    """Represents the binding of an URL pattern to a WebSocket view.

    Subclass of #::bocadillo.routing#BaseRoute.

    # Parameters
    pattern (str): an URL pattern.
    view (coroutine function):
        Should take as parameters a #::bocadillo.websockets#WebSocket object and
        any extracted route parameters.
    kwargs (any):
        passed when building the #::bocadillo.websockets#WebSocket object.
    """

    __slots__ = ("_ws_kwargs",)

    def __init__(self, pattern: str, view: WebSocketView, **kwargs):
        super().__init__(pattern, view)
        self._ws_kwargs = kwargs

    @classmethod
    def normalize(cls, view: Any) -> WebSocketView:
        return WebSocketView(view)

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send, **params
    ):
        ws = WebSocket(scope, receive=receive, send=send, **self._ws_kwargs)
        await self.view(ws, **params)


class WebSocketRouter(BaseRouter[WebSocketRoute, WebSocketView]):
    """A router for WebSocket routes.

    Subclass of #::bocadillo.routing#BaseRouter.
    """

    route_class = WebSocketRoute

    def _get_key(self, route: WebSocketRoute) -> str:
        return route.pattern

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

    __slots__ = ("http_router", "websocket_router")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.http_router = HTTPRouter()
        self.websocket_router = WebSocketRouter()

    def route(self, pattern: str, *, name: str = None, namespace: str = None):
        """Register a new route by decorating a view.

        # Parameters
        pattern (str): an URL pattern.
        methods (list of str):
            an optional list of HTTP methods.
            Defaults to `["get", "head"]`.
            Ignored for class-based views.
        name (str):
            an optional name for the route.
            If a route already exists for this name, it is replaced.
            Defaults to a snake-cased version of the view's name.
        namespace (str):
            an optional namespace for the route. If given, it is prefixed to
            the name and separated by a colon.
        """
        return self.http_router.route(
            pattern=pattern, name=name, namespace=namespace
        )

    def websocket_route(
        self,
        pattern: str,
        *,
        auto_accept: bool = True,
        value_type: str = None,
        receive_type: str = None,
        send_type: str = None,
        caught_close_codes: Tuple[int] = None,
    ):
        """Register a WebSocket route by decorating a view.

        # Parameters
        pattern (str): an URL pattern.

        # See Also
        - #::bocadillo.websockets#WebSocket for a description of keyword
        arguments.
        """
        # NOTE: use named keyword arguments instead of `**kwargs` to improve
        # their accessibility (e.g. for IDE discovery).
        return self.websocket_router.route(
            pattern=pattern,
            auto_accept=auto_accept,
            value_type=value_type,
            receive_type=receive_type,
            send_type=send_type,
            caught_close_codes=caught_close_codes,
        )

    def url_for(self, name: str, **kwargs) -> str:
        """Build the full URL path for a named #::bocadillo.routing#HTTPRoute.

        # Parameters
        name (str): the name of the route.
        kwargs (dict): route parameters.

        # Returns
        url (str): an URL path.

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
    ) -> NoReturn:
        """Redirect to another #::bocadillo.routing#HTTPRoute.

        This is only meant to be used inside an HTTP view.

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
