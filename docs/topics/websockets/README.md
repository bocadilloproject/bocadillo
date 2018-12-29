# Introduction

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
    message = await ws.receive()
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

Continue to learn more about to use WebSockets in Bocadillo.

[The API object]: ../api.md
[Routes and URL design]: ../http/routes-url-design.md
