# Accepting and closing connections

## Basic usage

- Accept a connection with `await ws.accept()`.
- Close a connection with `await ws.close()`, passing an optional close `code`.

## Async context manager syntax

Having to manually `accept` and `close` the connection can be cumbersome and error-prone.

To address this issue, the `ws` object can be used as an [asynchronous context manager] to `accept()` the connection on enter and `close()` it on exit.

```python
from bocadillo import API, WebSocket

api = API()

@api.websocket_route("/hello")
async def hello(ws: WebSocket):
    async with ws:
        # Connection accepted.
        # Receive or send messages…
        await ws.send("Hello, world!")
    # Connection closed.
    print("Connection closed as expected")
```

::: tip
It is safe to call `close()` within the WebSocket context, but calling it multiple times will raise a `RuntimeError`.

If you're not sure whether the connection has already been closed, use `await ws.ensure_closed()` instead.
:::

A rough equivalent to the above code snippet without using the `async with` syntax, including [error handling](./error-handling.md#how-exceptions-are-handled) code, would be:

```python
from bocadillo import API, WebSocket
from bocadillo.exceptions import WebSocketDisconnect

api = API()

@api.websocket_route("/hello")
async def hello(ws: WebSocket):
    await ws.accept()
    try:
        await ws.send("Hello, world!")
    except WebSocketDisconnect as exc:
        if exc.code in ws.caught_close_codes:
            print("Connection closed as expected")
        else:
            raise
    except:
        await ws.close(1011)
        raise
    else:
        await ws.close()
```

## Rejecting connection requests

It is possible to **reject** a WebSocket connection request by calling `await ws.reject()` before calling `await ws.accept()`. This has the same effect than closing the connection with a 403 close code, and complies with the ASGI specification.

You can use this to perform extra checks on the WebSocket request, such as access control checks:

```python
@api.websocket_route("/secret")
async def secret(ws: WebSocket):
    if ws.query_params.get("api_key") != "SECRET":
        await ws.reject()
    async with ws:
        # Proceed with an authorized client…
        pass
```

[asynchronous context manager]: https://www.python.org/dev/peps/pep-0492/#asynchronous-context-managers-and-async-with
