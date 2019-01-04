from starlette.websockets import WebSocketClose

from .websocket import WebSocketView, WebSocket
from ..asgi import Scope, Receive, Send
from ..meta import DocsMeta
from ..routing import BaseRouter, BaseRoute


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
