# Handling connections

## Automatic connection handling

In the standard WebSocket protocol, the server must **accept** a connection request when it receives one from a client, and **close** it when the communication ends.

By default, **Bocadillo automatically accepts and closes the connection request**. This reduces boilerplate and allows you to focus on receiving and sending messages.

Consider the following code:

```python
from bocadillo import App, WebSocket

@app.websocket_route("/echo")
async def echo(ws: WebSocket):
    ...
```

When a client connects to `ws://localhost:8000/echo`, Bocadillo will:

1. Accept the connection request.
2. Call the `echo` WebSocket view.
3. Close the connection request.

If something goes wrong when executing the view, Bocadillo will follow the protocol described in [error handling].

[error handling]: ./error-handling.md

For most applications, you don't need to know much more. Read on to learn about **advanced** connection handling.

## Manual connection handling <Badge type="warn" text="Advanced"/>

For advanced use cases, you can disable automatic connection handling by passing `auto_accept=False` to `@app.websocket_route()`.

This can be useful for a number of reasons, including:

- Performing advanced error handling.
- Conditionally [rejecting connection requests](#rejecting-connection-requests).

### Basic usage

When manually handling connections, you can:

- Accept a connection with `await ws.accept()`.
- Close a connection with `await ws.close()`, passing an optional close `code`.

```python
@app.websocket_route("/", auto_accept=False)
async def accept_close(ws: WebSocket):
    print("Going to accept connection…")
    await ws.accept()
    ...
    await ws.close()
    print("Connection closed normally!")
```

Code placed between `.accept()` and `.close()` is by definition executed within the _WebSocket context_.

An [asynchronous context manager] syntax is also available. The following code snippet is equivalent to the previous example:

```python
@app.websocket_route("/hello", auto_accept=False)
async def hello(ws: WebSocket):
    print("Going to accept connection…")
    async with ws:
        ...
    print("Connection closed normally!")
```

::: tip
It is safe to call `.close()` within the WebSocket context, but calling it multiple times will raise a `RuntimeError`.

When you're not sure whether the connection has already been closed, use `await ws.ensure_closed()` instead.
:::

::: tip
It is safe to use `async with ws:` if `auto_accept` is not set to `False`. This is done to ensure compatibility with < 0.13.1.
:::

### Rejecting connection requests

It is possible to **reject** a WebSocket connection request by calling `await ws.reject()` before calling `await ws.accept()`. This results in closing the connection with a 403 close code as described by the ASGI specification.

This can be used to perform extra checks on the connection request and reject it on failure.

The following example demonstrates implementing a decorator that rejects the connection request if a (very) naive API key check fails:

```python
from bocadillo import App

app = App()

def has_valid_api_key(view):
    async def with_permission_check(ws, **kwargs):
        if ws.query_params.get("api_key") != "SECRET":
            await ws.reject()
        else:
            await view(ws, **kwargs)
    return with_permission_check

@app.websocket_route("/secret", auto_accept=False)
@has_valid_api_key
async def secret(ws):
    async with ws:
        # Proceed with an authorized client…
        pass
```

[asynchronous context manager]: https://www.python.org/dev/peps/pep-0492/#asynchronous-context-managers-and-async-with
