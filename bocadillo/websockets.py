from typing import Awaitable, Callable, Optional, Any, Union, Tuple

from starlette.datastructures import URL
from starlette.websockets import (
    WebSocket as StarletteWebSocket,
    WebSocketDisconnect as _WebSocketDisconnect,
)

from .app_types import Event, Scope, Receive, Send
from .constants import WEBSOCKET_CLOSE_CODES


class WebSocket:
    """Represents a WebSocket connection.

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
    caught_close_codes (tuple of int):
        Close codes of `WebSocketDisconnect` exceptions that should be
        caught and silenced. Defaults to `(1000, 1001)`.
    args (any):
        Passed to the underlying Starlette `WebSocket` object. This is
        typically the ASGI `scope`, `receive` and `send` objects.
    """

    __default_receive_type__ = "text"
    __default_send_type__ = "text"

    def __init__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
        value_type: Optional[str] = None,
        receive_type: Optional[str] = None,
        send_type: Optional[str] = None,
        caught_close_codes: Optional[Tuple[int, ...]] = None,
    ):
        # NOTE: we use composition over inheritance here, because
        # we want to redefine `receive()` and `send()` but Starlette's
        # WebSocket class uses those in many other functions, which we
        # do not need / want to re-implement.
        # The compromise is the definition of delegated methods below.
        self._ws = StarletteWebSocket(scope, receive=receive, send=send)

        if caught_close_codes is None:
            caught_close_codes = (1000, 1001)
        if caught_close_codes is all:
            caught_close_codes = tuple(WEBSOCKET_CLOSE_CODES)
        self.caught_close_codes = caught_close_codes

        if value_type is not None:
            receive_type = send_type = value_type
        else:
            receive_type = receive_type or self.__default_receive_type__
            send_type = send_type or self.__default_send_type__

        self.receive_type = receive_type
        self.send_type = send_type

    @property
    def url(self) -> URL:
        """The URL which the WebSocket connection was made to.

        # See Also
        - [starlette.WebSocket.url](https://www.starlette.io/websockets/#url)
        """
        return self._ws.url

    # Connection handling.

    async def accept(self, subprotocol: str = None) -> None:
        """Accept the connection request.

        # Parameters
        subprotocol (str): a specific WebSocket subprotocol that should be expected from clients. Defaults to `None`.
        """
        return await self._ws.accept(subprotocol=subprotocol)

    async def reject(self):
        """Reject the connection request.

        This is equivalent to `.close(403)`.
        Calling this before `.accept()` has undefined behavior.
        """
        return await self.close(code=403)

    async def close(self, code: int = 1000) -> None:
        """Close the WebSocket connection.

        # Parameters
        code (int): a close code, defaults to `1000` (Normal Closure).

        # See Also
        - [CloseEvent specification](https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent)
        """
        return await self._ws.close(code=code)

    async def ensure_closed(self, code: int = 1000):
        """Close the connection if it has not been closed already."""
        try:
            await self.close(code=code)
        except RuntimeError:
            # Already closed.
            pass

    # Data reception/sending.

    async def receive_text(self) -> str:
        """Receive a message as text."""
        return await self._ws.receive_text()

    async def send_text(self, data: str):
        """Send a message as text."""
        return await self._ws.send_text(data)

    async def receive_bytes(self) -> bytes:
        """Receive a message a bytes."""
        return await self._ws.receive_bytes()

    async def send_bytes(self, data: bytes):
        """Send a message as bytes."""
        return await self._ws.send_bytes(data)

    async def receive_json(self) -> Union[dict, list]:
        """Receive a message as text and parse it to a JSON object.

        # Raises
        json.JSONDecodeError: if the received JSON is invalid.
        """
        return await self._ws.receive_json()

    async def send_json(self, data: Union[dict, list]):
        """Serialize an object to JSON and send it as text.

        # Raises
        TypeError: if the given `data` is not JSON serializable.
        """
        return await self._ws.send_json(data)

    async def receive_event(self) -> Event:
        """Receive a raw ASGI event."""
        return await self._ws.receive()

    async def send_event(self, event: Event):
        """Send a raw ASGI event."""
        return await self._ws.send(event)

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

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type == WebSocketDisconnect:
            # Client has closed the connection.
            # Returning `True` here silences the exception. See:
            # https://docs.python.org/3/reference/datamodel.html#object.__exit__
            return exc_val.code in self.caught_close_codes

        # Close with Internal Error if an unknown exception was raised.
        code = 1000 if exc_type is None else 1011
        # NOTE: view may have closed the WebSocket already, so we
        # must use ensure_closed().
        await self.ensure_closed(code)

    # Asynchronous iterator.

    async def __aiter__(self):
        while True:
            yield await self.receive()


WebSocketView = Callable[[WebSocket], Awaitable[None]]
WebSocketDisconnect = _WebSocketDisconnect
