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
It is possible to reject a WebSocket connection request by calling `close()` without calling `accept()`.

It is then recommended to provide an error code describing why the connection request was rejected. See the [CloseEvent] reference.
:::

## Automatically accepting and closing connections

Having to manually `accept` and `close` the connection can be cumbersome and error-prone.

To address this issue, the `ws` object can be used as an [asynchronous context manager]:

- The WebSocket connection is accepted on enter.
- It is closed on exit — even if an exception occurred.

This has the benefit of closing the WebSocket connection 

Still, what happens if the client disconnects before sending us a message? A `WebSocketDisconnect` exception will be raised, which means we'd have to catch it if we don't want our code to crash.

Luckily, the `ws` async context manager catches the exception for us.

As a result, the following code snippets are equivalent:

```python
from bocadillo import API, WebSocket

api = API()

@api.websocket_route("/hello")
async def hello(ws: WebSocket):
    async with ws:
        await ws.send("Hello, world!")
    print("Connection closed")
```

```python
from bocadillo import API, WebSocket
from bocadillo.exceptions import WebSocketDisconnect

api = API()

@api.websocket_route("/hello")
async def hello(ws: WebSocket):
    await ws.accept()
    try:
        await ws.send("Hello, world!")
    except WebSocketDisconnect:
        print("Connection closed")
    finally:
        await ws.close()
```

## Iterating over received messages

In our basic example, only one message was received and sent over the WebSocket; after that, we closed the connection.

What if we wanted to do this repeatedly, i.e. echo all messages that the client will send us through the WebSocket?

It turns out that `ws` is also an [asynchronous iterator], so we can iterate over the received messages like so:

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

By default, calling `await ws.receive()` and `ws.send()` will return and send text messages, i.e. Python `str` objects.

It is possible to specify how messages should be decoded (resp. encoded) by passing the `receive_type` (resp. `send_type`) argument to the `@api.websocket_route()` decorator.
 
 For convenience, `value_type` can be used to set `receive_type` and `send_type` to the same value.

The possible values for `receive_type`, `send_type` and `value_type` are listed below:

- `"text"`: decodes/encodes messages as `str`.
- `"bytes"`: decodes/encodes data as `bytes`.
- `"json"`: decodes with `json.loads()` and encodes with `json.dumps()`.

For example, here's an example of a WebSocket server that exchanges JSON messages with clients:

```python
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
In fact, `receive()` and `send()` are shortcuts that call the corresponding receive and send methods for the configured `receive_type` and `send_type`.

For example, if `receive_type="json"` then `await ws.receive()` is equivalent to `await ws.receive_json()`.

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

### Disabling automatic catching of `WebSocketDisconnect`

By default, the `ws` async context manager automatically catches and silences `WebSocketDisconnect` exceptions which are raised when the client closes the WebSocket.

To disable this behavior, pass `catch_disconnect=False` to `@api.websocket_route()`.


`catch_disconnect = False`

[The API object]: ../api.md
[Routes and URL design]: http://localhost:8080/topics/request-handling/routes-url-design.html#routes-and-url-design
[asynchronous context manager]: https://www.python.org/dev/peps/pep-0492/#asynchronous-context-managers-and-async-with
[asynchronous iterator]: https://www.python.org/dev/peps/pep-0492/#asynchronous-iterators-and-async-for
[WebSocket API reference]: ../../api/websockets.md
[ASGI Event]: https://asgi.readthedocs.io/en/latest/specs/main.html#events
[CloseEvent]: https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent
