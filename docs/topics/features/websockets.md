# WebSockets

**WebSockets** allow a web browser and a web server to communicate in a bi-directional way via a long-held, low-latency TCP socket connection. They are typically used to build **event-driven** and **real-time** web applications that involve things like notifications, instant messaging or other real-time features.

::: tip
As an introduction to WebSockets, we recommend Dion Misic's talk [A Beginner's Guide to WebSockets](https://www.youtube.com/watch?v=PjiXkJ6P9pQ) (Pycon 2018).
:::

Typically, WebSocket server applications are I/O-bound and need to deal with many concurrent client connections. This makes asynchronous programming a natural paradigm for implementing WebSocket servers.

As such, Bocadillo provides an easy-to-use and friendly API for building WebSocket servers.

## Prerequisites

Before you can use WebSockets, you need to install some extra dependencies. To do so, use the `websockets` pip extra when installing Bocadillo:

```bash
pip install bocadillo[websockets]
```

Once that's done, you're ready to go!

## A basic example

Let's learn by example and see how to create a WebSocket server that simply echoes a message:

```python
from bocadillo import API, WebSocket

api = API()

@api.websocket_route("/echo")
async def echo(ws: WebSocket):
    await ws.accept()
    message = ws.receive()
    await ws.send(f"You said: {message}")
    await ws.close()

if __name__ == "__main__":
    api.run()
```

Let's break this code down:

1. We create an `API` instance as usual. (If this is not familiar to you, see [The API object].)
2. We register a new **WebSocket route** using the `@api.websocket_route()` decorator. It works in a way similar to `@api.route()` for regular HTTP routes: we give it an URL pattern that will be matched against when an incoming WebSocket connection request is received.
3. We define a **WebSocket view**, i.e. an asynchronous function that takes a `WebSocket` object as its first parameter. [Route parameters are passed as extra arguments (see also [Routes and URL design]).
4. Inside the view:
    - We **accept** the connection request in order to complete the handshake with the client. The WebSocket connection is then established.
    - Then, we **receive** a text message from the WebSocket. If no message is available yet, the application will not block and will still be available for processing other requests. 
    - Next, we **send** a message ourselves to the client.
    - Lastly, we **close** the connection.

These four operations (accept, receive, send and close) are the basic building blocks of WebSocket views.

::: tip
It is possible to **reject** a WebSocket connection request by calling `close()` without calling `accept()`.

When doing so, you should provide a **close code** describing why the connection request was rejected, e.g. `await ws.close(1002)` for a protocol error. See the [CloseEvent] reference for the available close codes.
:::

## Error handling

WebSocket routes do not have advanced error handling mechanisms similar to those available for HTTP routes.

The only thing that Bocadillo does is ensuring that the client receives a 1011 (Unexpected Error) close event if an exception is raised on the server. This is done by catching exceptions raised in the view, closing the WebSocket and re-raising the exception. This applies whether you are using the [async context manager syntax](#async-context-manager-syntax) or not.

The only exception to this is [client-side connection closures](#handling-client-side-connection-closures).

## Async context manager syntax

### Usage

Having to manually `accept` and `close` the connection can be cumbersome and error-prone.

To address this issue, the `ws` object can be used as an [asynchronous context manager] to `accept()` the connection on enter and `close()` it on exit.

```python
async def hello(ws):
    async with ws:
        # Connection accepted.
        # Receive or send messages…
        pass
    # Connection closed.
```

::: tip
It is safe to call `close()` within the WebSocket context, but calling it multiple times will raise a `RuntimeError`.

If you're not sure whether the connection has already been closed, use `ensure_closed()` instead.
:::

### Handling client-side connection closures

When the client disconnects while we are trying to `receive()` a message, a `WebSocketDisconnect` exception is raised.

If you are using the `async with` syntax, this exception is automatically caught if the close code is either 1000 (Normal Closure) or 1001 (Going Away), both being considered successful closure codes.

For other close codes, the exception will propagate beyond the WebSocket's context. It is your responsibility to catch and handle it, if necessary.

::: tip
You can customize this behavior by passing a tuple of integers to the `caught_close_codes` parameter of `@api.websocket_route()`. The `all` Python built-in can be passed to catch all close codes. To not catch any close code, pass the empty tuple `()`.
:::

::: tip
The [constants](../../api/constants.md) module defines a dictionary of close codes which you can use for convenience.
:::

### Example

Here's an example usage of the `async with` syntax for WebSockets:

```python
from bocadillo import API, WebSocket

api = API()

@api.websocket_route("/hello")
async def hello(ws: WebSocket):
    async with ws:
        await ws.send("Hello, world!")
    print("Connection closed as expected")
```

A rough equivalent to the above code snippet without using the `async with` syntax, including error handling code, would be:

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

## Iterating over messages

In the [basic example](#a-basic-example), only one message was received and sent over the WebSocket, then we closed the connection.

What if we wanted to do this repeatedly, i.e. echo all messages that the client sends us through the WebSocket?

It turns out that `ws` is also an [asynchronous iterator], so we can iterate over each received message like so:

```python
async def echo(ws: WebSocket):
    async with ws:
        async for message in ws:
            await ws.send(f"You said: {message}")
```

This code is strictly equivalent to:

```python
async def echo(ws: WebSocket):
    async with ws:
        while True:
            message = await ws.receive()
            await ws.send(f"You said: {message}")
```

## Decoding and encoding messages

Messages are decoded or encoded as text messages by default: calling `receive()` and `send()` will return or expect `str` objects.

It is possible to specify how messages should be decoded (resp. encoded) by passing the `receive_type` (resp. `send_type`) argument to the `@api.websocket_route()` decorator.
 
 ::: tip
 For convenience, `value_type` can be used to set `receive_type` and `send_type` to the same value.
:::

The possible values for `receive_type`, `send_type` and `value_type` are:

- `"text"`: plain text as `str`.
- `"bytes"`: plain bytes as `bytes`.
- `"json"`: decodes with `json.loads()` and encodes with `json.dumps()`.
- `"event"`: raw ASGI events as `dict` (see [Using ASGI events](#using-asgi-events)).

For example, here's a WebSocket server that exchanges JSON messages with its clients:

```python{4}
from bocadillo import API, WebSocket

api = API()
@api.websocket_route("/ping-pong", value_type="json")
async def ping_pong(ws: WebSocket):
    async with ws:
        async for message in ws:
            resp = "pong" if message["type"] == "ping" else "ping"
            await ws.send({"type": resp})
```

::: tip
In fact, `receive()` and `send()` are shortcuts that call the corresponding receive and send methods for the WebSocket's `receive_type` and `send_type`.

For example, if `receive_type="json"` was given then `await ws.receive()` is equivalent to `await ws.receive_json()`.

See also the [WebSocket API reference].
:::

## Advanced usage

### Using ASGI events

It is possible to receive or send raw [ASGI events][ASGI Event] using the low-level `receive_event()` and `send_event()` methods.

For example, this is a rough equivalent of the [basic example](#a-basic-example) that uses ASGI events only:

```python
from bocadillo import API, WebSocket

@api.websocket_route("/echo")
async def echo(ws: WebSocket):
    await ws.send_event({"type": "websocket.accept"})
    event: dict = await ws.receive_event()
    message: str = event["text"]
    await ws.send_event({{"type": "websocket.send", "text": f"You said: {message}"}})
    await ws.send_event({"type": "websocket.close"})
```

[The API object]: ../api.md
[Routes and URL design]: http://localhost:8080/topics/request-handling/routes-url-design.html#routes-and-url-design
[asynchronous context manager]: https://www.python.org/dev/peps/pep-0492/#asynchronous-context-managers-and-async-with
[asynchronous iterator]: https://www.python.org/dev/peps/pep-0492/#asynchronous-iterators-and-async-for
[WebSocket API reference]: ../../api/websockets.md
[ASGI Event]: https://asgi.readthedocs.io/en/latest/specs/main.html#events
[CloseEvent]: https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent
