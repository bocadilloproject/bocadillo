from typing import Callable, List, Tuple

from starlette.middleware.lifespan import LifespanMiddleware

from .types import ASGIApp, ASGIAppInstance

EventHandler = Callable[[], None]


class LifespanMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._events: List[Tuple[str, EventHandler]] = []

    def on(self, event: str) -> Callable:
        """Register an event handler.

        # Parameters
        event (str):
            Either "startup" (when the server boots) or "shutdown" (when the
            server stops).
        """

        def decorate(f: EventHandler):
            self.add_event_handler(event, f)
            return f

        return decorate

    def add_event_handler(self, event: str, handler: EventHandler):
        self._events.append((event, handler))

    def _get_lifespan_middleware(self, app: ASGIApp):
        middleware = LifespanMiddleware(app)
        for event, func in self._events:
            middleware.add_event_handler(event, func)
        return middleware

    @staticmethod
    def lifespan_handler(scope: dict) -> ASGIAppInstance:
        """Strict implementation of the ASGI lifespan spec.

        This is required because the Starlette `LifespanMiddleware`
        does not send the `complete` responses.

        It runs before the Bocadillo app itself (which it wraps around),
        so this handler can just send the `complete` responses without
        doing anything special.
        """

        async def handle(receive, send):
            message = await receive()
            assert message["type"] == "lifespan.startup"
            await send({"type": "lifespan.startup.complete"})

            message = await receive()
            assert message["type"] == "lifespan.shutdown"
            await send({"type": "lifespan.shutdown.complete"})

        return handle

    def __call__(self, scope: dict):
        app = scope.pop("app")
        return self._get_lifespan_middleware(app)(scope)
