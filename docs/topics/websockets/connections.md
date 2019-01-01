# Accepting and closing connections

## Basic usage

Suppose your WebSocket view uses `ws` for the WebSocket object parameter. You can:

- Accept a connection with `await ws.accept()`.
- Close a connection with `await ws.close()`, passing an optional close `code`.

```python
from bocadillo import WebSocket

async def accept_close(ws: WebSocket):
    await ws.accept()
    await ws.close()
```

## Async context manager syntax

### Basic usage

Having to manually `accept` and `close` the connection can be cumbersome and error-prone.

To address this issue, the `ws` object can be used as an [asynchronous context manager] to `accept()` the connection on enter and `close()` it on exit.

```python
from bocadillo import API, WebSocket

api = API()

@api.websocket_route("/hello")
async def hello(ws: WebSocket):
    async with ws:
        print("Connected:", ws)
        person = await ws.receive()
        await ws.send(f"Hello, {person}!")
    print("Connection closed normally.")
```

::: tip
It is safe to call `close()` within the WebSocket context, but calling it multiple times will raise a `RuntimeError`.

When you're not sure whether the connection has already been closed, use `await ws.ensure_closed()` instead.
:::

### Try/except blocks considered useful

The previous code may raise an exception if the client closes the connection while we are running `await ws.receive()`.

We will see how this is handled in the next section. That said, note that **the async context manager syntax is *not* a replacement for error handling**.

In particular, code placed after an `async with ws` block will only execute if the connection was closed normally.

If something goes wrong either on any peer's side, it is *your* responsibility to handle the exception. In that case, wrapping the `async with` block around a `try/except/else/finally` block may be useful.

For example:

```python
from bocadillo import API, WebSocket

class Oops(Exception):
    pass

api = API()
connected = set()

@api.websocket_route("/hello")
async def hello(ws: WebSocket):
    try:
        async with ws:
            connected.add(ws)
            if await ws.receive() == "oops":
                raise Oops
            await ws.send("OK")
        # Only executed if `Oops` is not raised.
        print("OK")
    except Oops:
        # Exception error handling
        print("Oops!")
    finally:
        # Perform cleanup
        connected.remove(ws)
```

## Rejecting connection requests

It is possible to **reject** a WebSocket connection request by calling `await ws.reject()` before calling `await ws.accept()`. This has the same effect than closing the connection with a 403 close code, and complies with the ASGI specification.

A typical usage may be to perform extra checks on the connection request and reject it on failure.
 
The following example demonstrates implementing a decorator that rejects the connection request if a (very) naive API key check fails:

```python
from bocadillo import API

api = API()

def has_valid_api_key(view):
    async def with_permission_check(ws, **kwargs):
        if ws.query_params.get("api_key") != "SECRET":
            await ws.reject()
        else:
            await view(ws, **kwargs)
    return with_permission_check

@api.websocket_route("/secret")
@has_valid_api_key
async def secret(ws):
    async with ws:
        # Proceed with an authorized client…
        pass
```

[asynchronous context manager]: https://www.python.org/dev/peps/pep-0492/#asynchronous-context-managers-and-async-with
