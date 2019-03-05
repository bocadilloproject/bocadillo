# Server-Sent Events

[Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) (SSE) is a technique that allows a server to push messages to a client during a single, long-lived HTTP session.

SSE can be employed when the client needs to receive real-time updates from the server in a **uni-directional** fashion.

For example, a notification system or a live feed can easily be implemented using SSE.

::: tip
If you need bi-directional communication between the server and the client, you should take a look at [WebSockets](../websockets).
:::

## SSE basics

An SSE endpoint sends server-sent events over a single, long-lived connection.

Under the hood, this is very similar to [response streaming](./responses.md#streaming), except that:

- Messages must be encoded in a specific format known as the [event stream format](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
- Specific HTTP headers must be set so that the client (typically a JavaScript program that uses the [EventSource](https://developer.mozilla.org/en-US/docs/Web/API/EventSource) API) correctly decodes the messages.

Luckily, Bocadillo takes care of all this for you.

## Example

The following application exposes an SSE endpoint that simulates a feed of temperature data (10°C ± 2°C) sent periodically:

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

1. We import useful functions and classes, including the [server_event](/api/sse.md#server-event) helper (more on that shortly).
2. We create an application instance and a `/temperature-feed` route.
3. Inside the view, we define an **event stream** using the `@res.event_stream` decorator.
4. The event stream returns an **asynchronous generator** that yields SSE messages indefinitely. In this case, message data is JSON-encoded.

## Message formatting

> TODO
