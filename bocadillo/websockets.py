from typing import Awaitable, Callable, Optional, Any, Union

from starlette.websockets import (
    WebSocket as StarletteWebSocket,
    WebSocketDisconnect,
)


class _Delegated:
    """Descriptor to delegate a method to the underlying Starlette WebSocket.

    # See Also
    - [DEV tutorial](https://dev.to/dawranliou/writing-descriptors-in-python-36)
    """

    def __init__(self, name: str = None, websocket_attr: str = "_websocket"):
        self.source = name
        self.websocket_attr = websocket_attr

    def __set_name__(self, owner, name: str):
        # Use the declared attribute's name as default source attribute.
        if self.source is None:
            self.source = name

    def __get__(self, instance: "WebSocket", owner):
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
        Defaults to `default_receive_type`.
    send_type (str):
        The type of messages send over the WebSocket.
        Defaults to `default_send_type`.
    args (any):
        Passed to the underlying Starlette `WebSocket` object.
    kwargs (any):
        Passed to the underlying Starlette `WebSocket` object.

    # Attributes
    default_receive_type (str):
        Defaults to `"text"`.
    default_send_type (str):
        Defaults to `"text"`.
    """

    default_receive_type = "text"
    default_send_type = "text"

    def __init__(
        self,
        *args,
        value_type: Optional[str] = None,
        receive_type: Optional[str] = None,
        send_type: Optional[str] = None,
        **kwargs,
    ):
        # NOTE: we use composition over inheritance here, because
        # we want to redefine `receive()` and `send()` but Starlette's
        # WebSocket class uses those in many other functions, which we
        # do not need / want to re-implement.
        # The compromise is the definition of delegated methods below.
        self._websocket = StarletteWebSocket(*args, **kwargs)

        if value_type is not None:
            receive_type = send_type = value_type
        else:
            receive_type = receive_type or self.default_receive_type
            send_type = send_type or self.default_send_type
        self.receive_type = receive_type
        self.send_type = send_type

    # Methods delegated to the underlying Starlette WebSocket object.
    # TODO: see how this behaves with Pydoc-Markdown.
    # TODO: add type annotations.
    accept = _Delegated()
    close = _Delegated()
    receive_raw = _Delegated("receive")
    send_raw = _Delegated("send")
    receive_text = _Delegated()
    send_text = _Delegated()
    receive_bytes = _Delegated()
    send_bytes = _Delegated()
    receive_json = _Delegated()
    send_json = _Delegated()

    async def receive(self) -> Union[str, bytes, list, dict]:
        """Receive a message from the WebSocket.

        The message is decoded based on the `receive_type`.
        """
        receiver = getattr(self, f"receive_{self.receive_type}")
        return await receiver()

    async def send(self, message: Any):
        """Send a message over the WebSocket.

        The message is encoded based on the `send_type`.
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
            # Client disconnected, do not propagate exception.
            return True

    # Asynchronous iterator.

    async def __aiter__(self):
        while True:
            yield await self.receive()


WebSocketView = Callable[[WebSocket], Awaitable[None]]
