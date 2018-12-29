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
3. We define a **WebSocket view**, i.e. an asynchronous function that takes a `WebSocket` object as its first parameter. Route parameters are passed as extra arguments just like for HTTP routes (see also [Routes and URL design]).
4. Inside the view:
    - We **accept** the connection request in order to complete the handshake with the client. The WebSocket connection is then established.
    - Then, we **receive** a text message from the WebSocket. If no message is available yet, the view will suspend, allowing the server to process other requests until a message is received.
    - Next, we **send** a message to the client.
    - Lastly, we **close** the connection.

These four operations (accept, receive, send and close) are the basic building blocks of WebSocket views.

## How WebSocket requests are processed

When a client makes a request to your server with the `ws://` or `wss://` scheme, the following happens:

- The client and the frontend web server (Uvicorn in development and most likely [Gunicorn in production](../discussions/deployment.md)) perform a handshake to agree to [upgrade the protocol](https://developer.mozilla.org/en-US/docs/Web/HTTP/Protocol_upgrade_mechanism) to WebSocket. This is not handled by Bocadillo directly.
- The upgraded request is routed to Bocadillo and a `WebSocket` object is created out of it.
- Bocadillo tries to match the WebSocket's URL path against a registered WebSocket route. If none is found, the connection is closed with a 403 close code [as defined in the ASGI specification](https://asgi.readthedocs.io/en/latest/specs/www.html#close).
- Bocadillo calls the view attached to the route that matched. It must be an asynchronous function accepting the following parameters:
  - An instance of `WebSocket`.
  - Keyword arguments representing the extracted keyword arguments.
- If an exception is raised in the process, the connection is closed by following the procedure described in [Error handling](#error-handling).

## Accepting and closing connections

### Basic usage

- Accept a connection with `await ws.accept()`.
- Close a connection with `await ws.close()`, passing an optional close `code`.

### Async context manager syntax

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

A rough equivalent to the above code snippet without using the `async with` syntax, including [error handling](#how-exceptions-are-handled) code, would be:

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

### Rejecting connection requests

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

## Error handling

### How exceptions are handled

WebSocket routes do not have advanced error handling mechanisms similar to those available for HTTP routes.

The only thing that Bocadillo does is ensuring that the client receives a 1011 (Internal Error) close event if an exception is raised on the server. This is done by catching exceptions raised in the view and closing the WebSocket before re-raising the exception for further server-side processing. This applies whether you are using the [async context manager syntax](#async-context-manager-syntax) or not.

The only exception to this is [client-side connection closures](#handling-client-side-connection-closures).

### Returning errors

In the world of WebSockets, servers and clients notify one another of errors by closing the connection with an appropriate **close code**. This means that the canonical way of returning an error "response" (if there is such a thing) is to `close()` with an appropriate `code` as argument.

Which `code` should you use, then?

We recommend you use the **4000-4999 range** for custom close codes and provide the appropriate documentation for your clients. This range is indeed reserved to application use by the WebSocket standard. See also the [CloseEvent] reference page which notably lists all available close codes.

However, standard close codes in the 1000-1015 range may sometimes fit your use case. For these situations, you can refer to the dictionary of close codes available in the [constants](../../api/constants.md) module.

### Handling client-side connection closures

When the client disconnects while we are trying to `receive()` a message, a `WebSocketDisconnect` exception is raised.

This exception will be automatically caught (and silenced) if all the following conditions are met:

- The exception is raised within a WebSocket context (i.e. when using the `async with` syntax).
- The close code is 1000 (Normal Closure) or 1001 (Going Away), both being considered successful closure codes.

::: tip
You can customize which close codes are caught within the WebSocket context by passing a tuple of integers to the `caught_close_codes` parameter of `@api.websocket_route()`. The `all` Python built-in can be passed to catch all close codes. To not catch any close code, pass the empty tuple `()`.
:::

In other cases, you need to handle the exception yourself.

## Receiving and sending messages

### Basic usage

- Receive a message with `await ws.receive()`.
- Send a message with `await ws.send(message)`.

### Iterating over messages

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

### Decoding and encoding messages

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
[Routes and URL design]: ../../topics/request-handling/routes-url-design.html#routes-and-url-design
[asynchronous context manager]: https://www.python.org/dev/peps/pep-0492/#asynchronous-context-managers-and-async-with
[asynchronous iterator]: https://www.python.org/dev/peps/pep-0492/#asynchronous-iterators-and-async-for
[WebSocket API reference]: ../../api/websockets.md
[ASGI Event]: https://asgi.readthedocs.io/en/latest/specs/main.html#events
[CloseEvent]: https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent
