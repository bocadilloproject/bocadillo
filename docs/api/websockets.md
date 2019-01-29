# bocadillo.websockets

## WebSocket
```python
WebSocket(self, scope: dict, receive: Callable[[], Awaitable[MutableMapping[str, Any]]], send: Callable[[MutableMapping[str, Any]], NoneType], value_type: Union[str, NoneType] = None, receive_type: Union[str, NoneType] = None, send_type: Union[str, NoneType] = None, caught_close_codes: Union[Tuple[int], NoneType] = None)
```
Represents a WebSocket connection.

__Parameters__

- __value_type (str)__:
    The type of messages received or sent over the WebSocket.
    If given, overrides `receive_type` and `send_type`.
    Defaults to `None`.
- __receive_type (str)__:
    The type of messages received over the WebSocket.
    Defaults to `"text"`.
- __send_type (str)__:
    The type of messages send over the WebSocket.
    Defaults to `"text"`.
- __caught_close_codes (tuple of int)__:
    Close codes of `WebSocketDisconnect` exceptions that should be
    caught and silenced. Defaults to `(1000, 1001)`.
- __args (any)__:
    Passed to the underlying Starlette `WebSocket` object. This is
    typically the ASGI `scope`, `receive` and `send` objects.

### url
The URL which the WebSocket connection was made to.

__See Also__

- [starlette.WebSocket.url](https://www.starlette.io/websockets/#url)

### accept
```python
WebSocket.accept(self, subprotocol: str = None) -> None
```
Accept the connection request.

__Parameters__

- __subprotocol (str)__: a specific WebSocket subprotocol that should be expected from clients. Defaults to `None`.

### reject
```python
WebSocket.reject(self)
```
Reject the connection request.

This is equivalent to `.close(403)`.
Calling this before `.accept()` has undefined behavior.

### close
```python
WebSocket.close(self, code: int = 1000) -> None
```
Close the WebSocket connection.

__Parameters__

- __code (int)__: a close code, defaults to `1000` (Normal Closure).

__See Also__

- [CloseEvent specification](https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent)

### ensure_closed
```python
WebSocket.ensure_closed(self, code: int = 1000)
```
Close the connection if it has not been closed already.
### receive_text
```python
WebSocket.receive_text(self) -> str
```
Receive a message as text.
### send_text
```python
WebSocket.send_text(self, data: str)
```
Send a message as text.
### receive_bytes
```python
WebSocket.receive_bytes(self) -> bytes
```
Receive a message a bytes.
### send_bytes
```python
WebSocket.send_bytes(self, data: bytes)
```
Send a message as bytes.
### receive_json
```python
WebSocket.receive_json(self) -> Union[dict, list]
```
Receive a message as text and parse it to a JSON object.

__Raises__

- `json.JSONDecodeError`: if the received JSON is invalid.

### send_json
```python
WebSocket.send_json(self, data: Union[dict, list])
```
Serialize an object to JSON and send it as text.

__Raises__

- `TypeError`: if the given `data` is not JSON serializable.

### receive_event
```python
WebSocket.receive_event(self) -> MutableMapping[str, Any]
```
Receive a raw ASGI event.
### send_event
```python
WebSocket.send_event(self, event: MutableMapping[str, Any])
```
Send a raw ASGI event.
### receive
```python
WebSocket.receive(self) -> Union[str, bytes, list, dict]
```
Receive a message from the WebSocket.

Shortcut for `receive_<self.receive_type>`.

### send
```python
WebSocket.send(self, message: Any)
```
Send a message over the WebSocket.

Shortcut for `send_<self.send_type>`.

