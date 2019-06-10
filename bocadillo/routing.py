import typing

from starlette.datastructures import URL
from starlette.middleware.wsgi import WSGIMiddleware
from starlette.routing import Lifespan
from starlette.websockets import WebSocketClose

from .app_types import ASGIApp, EventHandler, Receive, Scope, Send
from .config import settings
from .errors import HTTPError
from .redirection import Redirect
from .urlparse import Parser
from .views import View
from .websockets import WebSocket, WebSocketView

_V = typing.TypeVar("_V")


def _join(prefix: str, path: str) -> str:
    return prefix + path


class BaseRoute(typing.Generic[_V]):
    def matches(self, scope: dict) -> typing.Tuple[bool, dict]:
        raise NotImplementedError

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        raise NotImplementedError


class Patterned(typing.Generic[_V]):
    __slots__ = ("_pattern", "_parser", "view")

    def __init__(self, pattern: str, view: _V):
        self._parser = Parser(pattern)
        self.view = view

    @property
    def pattern(self) -> str:
        return self._parser.pattern


class HTTPRoute(BaseRoute, Patterned[View]):
    def matches(self, scope: Scope) -> typing.Tuple[bool, Scope]:
        if scope["type"] != "http":
            return False, {}
        params = self._parser.parse(scope["path"])
        if params is None:
            return False, {}
        return True, {"path_params": params}

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        req, res = scope["req"], scope["res"]
        await self.view(req, res, **scope["path_params"])


class WebSocketRoute(BaseRoute, Patterned[WebSocketView]):
    __slots__ = ("ws_kwargs",)

    def __init__(self, pattern: str, view: WebSocketView, **kwargs):
        super().__init__(pattern, view)
        self.ws_kwargs = kwargs

    def matches(self, scope: Scope) -> typing.Tuple[bool, Scope]:
        if scope["type"] != "websocket":
            return False, {}
        params = self._parser.parse(scope["path"])
        if params is None:
            return False, {}
        return True, {"path_params": params}

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        ws = WebSocket(scope, receive, send, **self.ws_kwargs)
        await self.view(ws, **scope["path_params"])


class Mount(BaseRoute):
    def __init__(self, path: str, app: ASGIApp):
        if not path.startswith("/"):
            path = "/" + path
        path = path.rstrip("/")

        self.app = app
        self.path = path
        self._parser = Parser(self.path + "/{path:path}")

    def matches(self, scope: dict) -> typing.Tuple[bool, dict]:
        path = scope["path"]

        if path == self.path + "/":
            params = {"path": ""}
        else:
            params = self._parser.parse(path)

        if params is not None:
            remaining_path = "/" + params["path"]
            matched_path = path[: -len(remaining_path)]
            child_scope = {
                "path": remaining_path,
                "root_path": scope.get("root_path", "") + matched_path,
            }
            return True, child_scope

        return False, {}

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except TypeError:
            app = WSGIMiddleware(self.app)
            await app(scope, receive, send)


class Router:
    __slots__ = ("routes", "lifespan")

    def __init__(self):
        self.routes: typing.List[BaseRoute] = []
        self.lifespan = Lifespan()

    def add_route(self, route: BaseRoute) -> None:
        self.routes.append(route)

    def include(self, other: "Router", prefix: str = ""):
        """Include the routes of another router."""
        for route in other.routes:
            assert isinstance(route, (HTTPRoute, WebSocketRoute, Mount))
            if prefix:
                if isinstance(route, HTTPRoute):
                    route = HTTPRoute(
                        pattern=_join(prefix, route.pattern), view=route.view
                    )
                elif isinstance(route, WebSocketRoute):
                    route = WebSocketRoute(
                        pattern=_join(prefix, route.pattern),
                        view=route.view,
                        **route.ws_kwargs,
                    )
                else:
                    route = Mount(path=_join(prefix, route.path), app=route.app)
            self.add_route(route)

    def mount(self, path: str, app: ASGIApp):
        """Mount an ASGI or WSGI app at the given path."""
        return self.add_route(Mount(path, app))

    def on(self, event: str, handler: typing.Optional[EventHandler] = None):
        if handler is None:

            def register(func):
                self.lifespan.add_event_handler(event, func)
                return func

            return register

        self.lifespan.add_event_handler(event, handler)
        return handler

    def route(self, pattern: str, methods: typing.List[str] = None):
        """Register an HTTP route by decorating a view.

        # Parameters
        pattern (str): an URL pattern.
        """

        def decorate(view: typing.Any) -> HTTPRoute:
            view = View(view, methods=methods)
            route = HTTPRoute(pattern, view)
            self.add_route(route)
            return route

        return decorate

    def websocket_route(
        self,
        pattern: str,
        *,
        auto_accept: bool = True,
        value_type: str = None,
        receive_type: str = None,
        send_type: str = None,
        caught_close_codes: typing.Tuple[int] = None,
    ):
        """Register a WebSocket route by decorating a view.

        See #::bocadillo.websockets#WebSocket for a description of keyword
        parameters.

        # Parameters
        pattern (str): an URL pattern.
        """

        def decorate(view: typing.Any) -> WebSocketRoute:
            view = WebSocketView(view)
            route = WebSocketRoute(
                pattern,
                view,
                auto_accept=auto_accept,
                value_type=value_type,
                receive_type=receive_type,
                send_type=send_type,
                caught_close_codes=caught_close_codes,
            )
            self.add_route(route)
            return route

        return decorate

    def _find_route(self, scope: dict) -> typing.Optional[BaseRoute]:
        for route in self.routes:
            matches, child_scope = route.matches(scope)
            if matches:
                scope.update(child_scope)
                return route
        return None

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        scope["send"] = send  # See: `RequestResponseMiddleware`.

        if scope["type"] == "lifespan":
            await self.lifespan(scope, receive, send)
            return

        route = self._find_route(scope)

        if route is not None:
            try:
                await route(scope, receive, send)
                return
            except Redirect as exc:
                scope["res"] = exc.response
                return

        try_http_redirect = (
            scope["type"] == "http"
            and not scope["path"].endswith("/")
            and redirect_trailing_slash_enabled()
        )

        if try_http_redirect:
            redirect_scope = dict(scope)
            redirect_scope["path"] += "/"
            route = self._find_route(redirect_scope)
            if route is not None:
                redirect_url = URL(scope=redirect_scope)
                scope["res"] = Redirect(str(redirect_url)).response
                return

        if scope["type"] == "websocket":
            await WebSocketClose(code=403)(receive, send)
            return

        raise HTTPError(404)


def redirect_trailing_slash_enabled() -> bool:
    return settings.get("REDIRECT_TRAILING_SLASH", True)
