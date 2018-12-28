# bocadillo.websockets

## WebSocket
```python
WebSocket(self, *args, value_type: Union[str, NoneType] = None, receive_type: Union[str, NoneType] = None, send_type: Union[str, NoneType] = None, caught_close_codes: Union[Tuple[int], NoneType] = None)
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

### accept
```python
WebSocket.accept(self, subprotocol: List[str] = None) -> None
```


Alias of `accept` on [Starlette.websockets.WebSocket](https://www.starlette.io/websockets/).
### close
```python
WebSocket.close(self, code: int = 1000) -> None
```


Alias of `close` on [Starlette.websockets.WebSocket](https://www.starlette.io/websockets/).
### receive_bytes
```python
WebSocket.receive_bytes(self) -> bytes
```


Alias of `receive_bytes` on [Starlette.websockets.WebSocket](https://www.starlette.io/websockets/).
### receive_json
```python
WebSocket.receive_json(self) -> Any
```


Alias of `receive_json` on [Starlette.websockets.WebSocket](https://www.starlette.io/websockets/).
### receive_text
```python
WebSocket.receive_text(self) -> str
```


Alias of `receive_text` on [Starlette.websockets.WebSocket](https://www.starlette.io/websockets/).
### send_bytes
```python
WebSocket.send_bytes(self, data: bytes) -> None
```


Alias of `send_bytes` on [Starlette.websockets.WebSocket](https://www.starlette.io/websockets/).
### send_json
```python
WebSocket.send_json(self, data: Any) -> None
```


Alias of `send_json` on [Starlette.websockets.WebSocket](https://www.starlette.io/websockets/).
### send_text
```python
WebSocket.send_text(self, data: str) -> None
```


Alias of `send_text` on [Starlette.websockets.WebSocket](https://www.starlette.io/websockets/).
### receive_event
```python
WebSocket.receive_event(self) -> MutableMapping[str, Any]
```


Alias of `receive` on [Starlette.websockets.WebSocket](https://www.starlette.io/websockets/).
### send_event
```python
WebSocket.send_event(self, event: MutableMapping[str, Any])
```


Alias of `send` on [Starlette.websockets.WebSocket](https://www.starlette.io/websockets/).
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

### ensure_closed
```python
WebSocket.ensure_closed(self, code: int = 1000)
```
Close the connection if it has not been closed already.

__Parameters__

- __code (int)__: a close code, defaults to `1000`.

