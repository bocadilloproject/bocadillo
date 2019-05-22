# Server-Sent Events

Bocadillo has built-in support for [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) (a.k.a SSE), a technique that allows servers to push real-time updates to clients. For example, a notification system or a live feed can easily be implemented using SSE.

Please note that SSE is **unidirectional**: only the server can send messages, not the client. Besides, [browser support is limited](https://caniuse.com/#feat=eventsource&search=server%20sent%20events). If you need bi-directional asynchronous communication between the server and the client, take a look at [WebSockets](/guide/websockets.md).

## SSE basics

An SSE endpoint sends messages (known as _server events_) over a single, long-lived connection in order to notify the client that data has changed or that new data is available.

<b-figure src="/sse.png" caption="After the initial request, Bocadillo can push SSE events to the client."/>

Under the hood, this is very similar to [response streaming](/guide/responses.md#streaming), except that:

- Messages must be encoded in a specific format known as the [event stream format](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
- Specific HTTP headers must be set so that the connection is kept alive, and that the client (typically a JavaScript program written using the [EventSource](https://developer.mozilla.org/en-US/docs/Web/API/EventSource) API) correctly decodes messages.

Luckily, Bocadillo helps you with all of these tasks.

## Example

The following example exposes an SSE endpoint that simulates a feed of temperature data:

```python
from asyncio import sleep
import random
from bocadillo import App, server_event

app = App()

@app.route("/temperature-feed")
async def temperature_feed(req, res):
    @res.event_stream
    async def send_temperature_data():
        while True:
            temperature = await get_temperature()
            yield server_event(json={"temperature": temperature})
            await sleep(0.01)

async def get_temperature():
    # TODO: get this from a sensor or something?
    return 10 + 2 * (2 * random.random() - 1)
```

Let's break this code down:

1. We import useful functions and classes, including the [`server_event`] helper (more on that shortly).
2. We create an application instance and a `/temperature-feed` route.
3. Inside the view, we define an **event stream** using the [`@res.event_stream`][res-event-stream] decorator.
4. The event stream is an **asynchronous generator** that `yield`s SSE messages indefinitely. In this case, messages are JSON-encoded.

[`server_event`]: /api/sse.md#server-event
[res-event-stream]: /api/response.md#event-stream

## Messages

The [Event Stream specification](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format) describes the fields that an SSE message can contain.

In theory, you could write the messages by hand and `yield` them in the [`@res.event_stream`][res-event-stream] generator, but this would be tedious. Instead, use the [`server_event`] helper to make sure you produce spec-compliant messages.

For example, here's how the temperature event looks like:

```python
>>> from bocadillo import server_event
>>> server_event(json={"temperature": 10.5})
'data: {"temperature": 10.5}\n\n'
```

As you can see, the JSON message has been serialized (encoded) and set as the `data` field for the message. It is followed by two empty lines, as required by the SSE specification.

### Sending data

Using the [`server_event`] helper, data can be sent either:

- In plain text using the `data` parameter:

```python
server_event(data="Hello, SSE!")
```

Pass an iterable for multi-line data:

```python
server_event(data=["Hello, SSE!", "Nice to meet you."])
```

- As JSON using the `json` parameter:

```python
server_event(json={"message": "Hello, SSE!"})
```

Note: the SSE specification does not allow to send binary data.

### Naming events

As per the SSE spec, you can give a name to a server event to allow clients to distinguish between them. Here's an example:

```python
server_event("greeting", data="Hello, SSE!")
```

## Client disconnects

Event streams being just streams with some extra formatting, Bocadillo handles client disconnections just like in [HTTP response streaming](/guide/responses.md#streaming):

1. By default, client disconnections stop the event stream.
2. To perform extra cleanup, pass `raise_on_disconnect=True` and handle the `ClientDisconnect` exception. You should make sure that no other messages are sent in the future.

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
