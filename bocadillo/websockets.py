from typing import Awaitable, Callable, Optional, Any, Union

from starlette.websockets import WebSocket as StarletteWebSocket

from .app_types import Event
from .exceptions import WebSocketDisconnect

_STARLETTE_WEBSOCKET_DOCS = (
    "[Starlette.websockets.WebSocket](https://www.starlette.io/websockets/)"
)


def _get_alias_docs(name: str) -> str:
    return f"\n\nAlias of `{name}` on {_STARLETTE_WEBSOCKET_DOCS}."


class _Delegated:
    """Descriptor to delegate a method to the underlying Starlette WebSocket.

    # See Also
    - [Descriptors](https://docs.python.org/3/reference/datamodel.html#implementing-descriptors)
    """

    def __init__(self, websocket_attr: str = "_websocket"):
        self.websocket_attr = websocket_attr
        self._docs_imported = False

    def __set_name__(self, owner, name: str):
        # Use the declared attribute's name as source attribute name.
        self.source = name

    def __get__(self, instance: Optional["WebSocket"], owner):
        if instance is None:  # pragma: no cover
            # Class attribute access.
            # NOTE: used by Pydoc-Markdown when generating docs.
            obj = getattr(StarletteWebSocket, self.source)
            if not self._docs_imported:
                obj.__doc__ = (obj.__doc__ or "") + _get_alias_docs(self.source)
                self._docs_imported = True
            return obj
        else:
            # Instance attribute access.
            return getattr(getattr(instance, self.websocket_attr), self.source)


class WebSocket:
    """Represents a WebSocket connection.

    Available message types: `["text", "bytes", "json"]`.

    # Parameters
    value_type (str):
        The type of messages received or sent over the WebSocket.
        If given, overrides `receive_type` and `send_type`.
        Defaults to `None`.
    receive_type (str):
        The type of messages received over the WebSocket.
        Defaults to `"text"`.
    send_type (str):
        The type of messages send over the WebSocket.
        Defaults to `"text"`.
    catch_disconnect (bool):
        Whether `WebSocketDisconnect` exceptions should be caught and silenced.
        Defaults to `True`.
    args (any):
        Passed to the underlying Starlette `WebSocket` object.
    kwargs (any):
        Passed to the underlying Starlette `WebSocket` object.
    """

    __default_receive_type__ = "text"
    __default_send_type__ = "text"

    def __init__(
        self,
        *args,
        value_type: Optional[str] = None,
        receive_type: Optional[str] = None,
        send_type: Optional[str] = None,
        catch_disconnect: bool = True,
        **kwargs,
    ):
        # NOTE: we use composition over inheritance here, because
        # we want to redefine `receive()` and `send()` but Starlette's
        # WebSocket class uses those in many other functions, which we
        # do not need / want to re-implement.
        # The compromise is the definition of delegated methods below.
        self._websocket = StarletteWebSocket(*args, **kwargs)
        self.catch_disconnect = catch_disconnect

        if value_type is not None:
            receive_type = send_type = value_type
        else:
            receive_type = receive_type or self.__default_receive_type__
            send_type = send_type or self.__default_send_type__
        self.receive_type = receive_type
        self.send_type = send_type

    # Methods delegated to the underlying Starlette WebSocket object.
    # TODO: add type annotations.
    accept = _Delegated()
    close = _Delegated()
    receive_text = _Delegated()
    send_text = _Delegated()
    receive_bytes = _Delegated()
    send_bytes = _Delegated()
    receive_json = _Delegated()
    send_json = _Delegated()

    async def receive_event(self) -> Event:
        return await self._websocket.receive()

    receive_event.__doc__ = _get_alias_docs("receive")

    async def send_event(self, event: Event):
        return await self._websocket.send(event)

    send_event.__doc__ = _get_alias_docs("send")

    async def receive(self) -> Union[str, bytes, list, dict]:
        """Receive a message from the WebSocket.

        Shortcut for `receive_<self.receive_type>`.
        """
        receiver = getattr(self, f"receive_{self.receive_type}")
        return await receiver()

    async def send(self, message: Any):
        """Send a message over the WebSocket.

        Shortcut for `send_<self.send_type>`.
        """
        sender = getattr(self, f"send_{self.send_type}")
        return await sender(message)

    # Asynchronous context manager.

    async def __aenter__(self, *args, **kwargs):
        await self.accept()
        return self

    async def __aexit__(self, exc_type, *args, **kwargs):
        await self.close()
        if exc_type == WebSocketDisconnect:
            # Client disconnected. Returning `True` here will silence
            # the exception. See:
            # https://docs.python.org/3/reference/datamodel.html#object.__exit__
            return self.catch_disconnect

    # Asynchronous iterator.

    async def __aiter__(self):
        while True:
            yield await self.receive()


WebSocketView = Callable[[WebSocket], Awaitable[None]]
