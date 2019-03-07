# Server-Sent Events

[Server-Sent Events][sse] (SSE) is a technique that allows a server to push messages to a client asynchronously using a single, long-lived connection.

[sse]: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events

SSE is **uni-directional** and can be employed when the client needs to receive real-time updates from the server.

For example, a notification system or a live feed can easily be implemented using SSE.

::: tip
If you need bi-directional asynchronous communication between the server and the client, you should take a look at [WebSockets](../websockets).
:::

## SSE basics

An SSE endpoint sends messages (known as _server events_) over a single, long-lived connection in order to notify the client that data has changed or that new data is available.

Under the hood, this is very similar to [response streaming](./responses.md#streaming), except that:

- Messages must be encoded in a specific format known as the [event stream format](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
- Specific HTTP headers must be set so that: a) the connection is [kept alive](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Keep-Alive), and b) the client (typically a JavaScript program that uses the [EventSource](https://developer.mozilla.org/en-US/docs/Web/API/EventSource) API) correctly decodes the messages.

Luckily, Bocadillo takes care of all this for you.

## Example

The following example exposes an SSE endpoint that simulates a feed of temperature data (10°C ± 2°C) sent periodically:

```python
# 1.
from asyncio import sleep
import random

from bocadillo import App, server_event

# 2.
app = App()

@app.route("/temperature-feed")
async def temperature_feed(req, res):
    # 3.
    @res.event_stream
    async def send_temperature_data():
        # 4.
        while True:
            temperature = await get_temperature()
            yield server_event(json={"temperature": temperature})
            await sleep(0.01)

async def get_temperature():
    # TODO: get this from a sensor or something?
    return 10 + 2 * (2 * random.random() - 1)

if __name__ == "__main__":
    app.run()
```

Let's break this code down:

1. We import useful functions and classes, including the [server_event] helper (more on that shortly).
2. We create an application instance and a `/temperature-feed` route.
3. Inside the view, we define an **event stream** using the [@res.event_stream][res-event-stream] decorator, which sets the required HTTP headers on the response.
4. The event stream returns an **asynchronous generator** that yields SSE messages indefinitely. In this case, message data is JSON-encoded.

[server_event]: /api/sse.md#server-event
[res-event-stream]: /api/response.md#event-stream

## Messages

SSE is all about pushing messages to the client. This section describes how you can build SSE messages in Bocadillo.

### Complying with the specification

The [Event Stream specification][sse-format] describes the fields a Server-Sent Event can contain.

In theory, you could write the messages by hand and `yield` them in the [@res.event_stream][res-event-stream] generator. But we figured this would be tedious, so we've built the [server_event] helper. Use it to make sure you produce spec-compliant messages.

[sse-format]: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format

For example, here's how the temperature event looks like:

```python
>>> from bocadillo import server_event
>>> server_event(json={"temperature": 10.5})
'data: {"temperature": 10.5}\n\n'
```

As you can see, JSON data has been serialized (encoded) and set as the `data` field for the message. It is followed by two empty lines, as required by the SSE specification.

### Sending data

Data can be sent either:

- In plain text using the `data` parameter:

```python
server_event(data="Hello, SSE!")

# Pass an iterable for multi-line data
server_event(data=["Hello, SSE!", "Nice to meet you."])
```

- As JSON using the `json` parameter:

```python
server_event(json={"message": "Hello, SSE!"})
```

### Naming events

If your SSE endpoint sends events of various kinds, the client needs a way to distinguish them. You can achieve this by giving the events a name, e.g.:

```python
server_event("greeting", data="Hello, SSE!")
```

## Error handling

Event streams being just streams with some extra formatting, Bocadillo handles client disconnections no differently than for HTTP response streaming. You can read about this in [Handling client disconnections](/guides/http/responses.md#handling-client-disconnections).

This means that:

1. By default, client disconnections stop the event stream.
2. To perform extra cleanup, pass `raise_on_disconnect=True` and handle the `ClientDisconnect` exception, making sure that no other messages are sent in the future.

Here's an example of performing extra cleanup when the client disconnects:

```python
from bocadillo import App, ClientDisconnect

app = App()

@app.route("/temperature-feed")
async def temperature_feed(req, res):
    @res.event_stream(raise_on_disconnect=True)
    async def send_temperature_data():
        try:
            while True:
                temperature = await get_temperature()
                yield server_event(json={"temperature": temperature})
                await sleep(0.01)
        except ClientDisconnect:
            print("Releasing sensor resources…")
```
