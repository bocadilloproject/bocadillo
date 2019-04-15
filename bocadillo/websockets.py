import traceback
import typing

import typesystem
from starlette.datastructures import URL, Headers, QueryParams
from starlette.websockets import WebSocket as StarletteWebSocket
from starlette.websockets import WebSocketDisconnect as _WebSocketDisconnect

from .app_types import Event, Receive, Scope, Send
from .compat import asyncnullcontext, check_async
from .constants import WEBSOCKET_CLOSE_CODES
from .converters import ViewConverter, convert_arguments
from .injection import consumer


class WebSocket:
    """Represents a WebSocket connection.

    See also [WebSockets](/guides/websockets/).

    # Parameters
    scope (dict): ASGI scope.
    receive (callable): ASGI receive function.
    send (callable): ASGI send function.
    auto_accept (bool):
        whether to automatically accept the WebSocket connection request.
        Defaults to `True`. If `False` is passed, the connection must be 
        accepted via `.accept()` or an `async with` block. Useful to
        perform conditionally `.reject()` a connection request or perform
        advanced error handling.
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

    # Attributes
    url (str-like): the URL which the WebSocket connection was made to.
    headers (dict): headers attached to the connection request.
    query_params (dict): parsed query parameters.
    """

    __slots__ = (
        "_ws",
        "caught_close_codes",
        "auto_accept",
        "__accepted",
        "receive_type",
        "send_type",
    )

    __default_receive_type__ = "text"
    __default_send_type__ = "text"

    url: URL
    headers: Headers
    query_params: QueryParams

    def __init__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
        auto_accept: bool = True,
        value_type: str = None,
        receive_type: str = None,
        send_type: str = None,
        caught_close_codes: typing.Tuple[int, ...] = None,
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

        self.auto_accept = auto_accept
        self.__accepted = False

        if value_type is not None:
            receive_type = send_type = value_type
        else:
            receive_type = receive_type or self.__default_receive_type__
            send_type = send_type or self.__default_send_type__

        self.receive_type = receive_type
        self.send_type = send_type

    def __getattr__(self, name: str) -> typing.Any:
        return getattr(self._ws, name)

    def __getitem__(self, name: str) -> typing.Any:
        return self._ws.__getitem__(name)

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

    async def receive_json(self) -> typing.Union[dict, list]:
        """Receive a message as text and parse it to a JSON object.

        # Raises
        json.JSONDecodeError: if the received JSON is invalid.
        """
        return await self._ws.receive_json()

    async def send_json(self, data: typing.Union[dict, list]):
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

    async def receive(self) -> typing.Union[str, bytes, list, dict]:
        """Receive a message from the WebSocket.

        Shortcut for `receive_<self.receive_type>`.
        """
        receiver = getattr(self, f"receive_{self.receive_type}")
        return await receiver()

    async def send(self, message: typing.Any):
        """Send a message over the WebSocket.

        Shortcut for `send_<self.send_type>`.
        """
        sender = getattr(self, f"send_{self.send_type}")
        return await sender(message)

    # Asynchronous context manager.

    async def __aenter__(self, *args, **kwargs):
        if not self.__accepted:
            await self.accept()
            self.__accepted = True
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


class WebSocketConverter(ViewConverter):
    def get_query_params(self, args: tuple, kwargs: dict) -> dict:
        ws: WebSocket = args[0]
        return ws.query_params


class WebSocketView:

    __slots__ = ("func",)

    def __init__(self, func: typing.Callable):
        check_async(
            func,
            reason=f"WebSocket view '{func.__name__}' must be asynchronous",
        )
        func = convert_arguments(func, converter_class=WebSocketConverter)
        func = consumer(func)
        self.func = func

    async def __call__(self, ws: WebSocket, **params):
        context = ws if ws.auto_accept else asyncnullcontext()
        try:
            async with context:
                try:
                    await self.func(ws, **params)  # type: ignore
                except typesystem.ValidationError:
                    await ws.ensure_closed(403)
                    traceback.print_exc()
        except BaseException:
            traceback.print_exc()
            await ws.ensure_closed(1011)
            raise


WebSocketDisconnect = _WebSocketDisconnect
