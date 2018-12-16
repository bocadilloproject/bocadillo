from typing import Callable, List, Tuple, Optional

from starlette.middleware.lifespan import LifespanMiddleware

from .types import ASGIApp, ASGIAppInstance

EventHandler = Callable[[], None]


class EventsMixin:
    """Provide server event handling capabilities."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._events: List[Tuple[str, EventHandler]] = []

    def on(self, event: str, handler: Optional[EventHandler] = None):
        """Register an event handler.

        # Parameters
        event (str):
            Either "startup" (when the server boots) or "shutdown" (when the
            server stops).
        handler (callback, optional):
            The event handler. If not given, this should be used as a
            decorator.
        """

        if handler is not None:
            self._add_event_handler(event, handler)
            return
        else:

            def decorate(f: EventHandler):
                self._add_event_handler(event, f)
                return f

            return decorate

    def _add_event_handler(self, event: str, handler: EventHandler):
        self._events.append((event, handler))

    def _get_lifespan_middleware(self, app: ASGIApp):
        middleware = LifespanMiddleware(app)
        for event, func in self._events:
            middleware.add_event_handler(event, func)
        return middleware

    def handle_lifespan(self, scope: dict) -> ASGIAppInstance:
        # Strict implementation of the ASGI lifespan spec.
        # This is required because the Starlette `LifespanMiddleware`
        # does not send the `complete` responses.

        async def app(receive, send):
            message = await receive()
            assert message["type"] == "lifespan.startup"
            await send({"type": "lifespan.startup.complete"})

            message = await receive()
            assert message["type"] == "lifespan.shutdown"
            await send({"type": "lifespan.shutdown.complete"})

        return self._get_lifespan_middleware(lambda s: app)(scope)
