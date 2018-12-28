# bocadillo.websockets

## WebSocket
```python
WebSocket(self, *args, value_type: Union[str, NoneType] = None, receive_type: Union[str, NoneType] = None, send_type: Union[str, NoneType] = None, catch_disconnect: bool = True, **kwargs)
```
Represents a WebSocket connection.

Available message types: `["text", "bytes", "json"]`.

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
- __catch_disconnect (bool)__:
    Whether `WebSocketDisconnect` exceptions should be caught and silenced.
    Defaults to `True`.
- __args (any)__:
    Passed to the underlying Starlette `WebSocket` object.
- __kwargs (any)__:
    Passed to the underlying Starlette `WebSocket` object.

### accept
```python
WebSocket.accept(self, subprotocol: List[str] = None) -> None
```

### close
```python
WebSocket.close(self, code: int = 1000) -> None
```

### receive_bytes
```python
WebSocket.receive_bytes(self) -> bytes
```

### receive_json
```python
WebSocket.receive_json(self) -> Any
```

### receive_text
```python
WebSocket.receive_text(self) -> str
```

### send_bytes
```python
WebSocket.send_bytes(self, data: bytes) -> None
```

### send_json
```python
WebSocket.send_json(self, data: Any) -> None
```

### send_text
```python
WebSocket.send_text(self, data: str) -> None
```

### receive_raw
```python
WebSocket.receive_raw(self) -> MutableMapping[str, Any]
```
Receive a raw ASGI message.

__Returns__

`message (dict)`: an ASGI message.

### send_raw
```python
WebSocket.send_raw(self, message: MutableMapping[str, Any])
```
Send a raw ASGI message.

__Parameters__

- __message (dict)__: an ASGI message.

### receive
```python
WebSocket.receive(self) -> Union[str, bytes, list, dict]
```
Receive a message from the WebSocket.

Shortcut for `receive_{receive_type}`.

### send
```python
WebSocket.send(self, message: Any)
```
Send a message over the WebSocket.

Shortcut for `send_{send_type}`.

