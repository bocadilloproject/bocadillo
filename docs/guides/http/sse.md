# Server-Sent Events

[Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) (SSE) is a technique that allows a server to push messages to a client as new data is being made available.

SSE can be employed when the client needs to receive real-time updates from the server. For example, a notification system or live feed could be implemented in this manner.

::: tip
If you need bi-directional communication between the server and the client, [WebSocket](../websockets) is most likely a better option.
:::

## SSE basics

Building an SSE endpoint is relatively simple. It is [HTTP streaming](./responses.md#streaming) with messages encoded in a specific format — the [event stream format](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).

Here's a basic SSE endpoint that sends a feed of noisy temperature data (10°C ± 2°C) at random intervals:

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
            temperature = peek_temperature()
            yield server_event(json={"temperature": temperature})
            await sleep(random.random())

def peek_temperature():
    return 10 + 2 * (2 * random.random() - 1)

if __name__ == "__main__":
    app.run()
```

Let's break this code down:

1. We import useful functions and classes, including the `server_event` helper (more on that shortly).
2. We create an application instance and a `/temperature-feed` route.
3. Inside the view, we define an **event stream** using the `@res.event_stream` decorator.
4. The event stream is an **asynchronous generator** that yields `server_event` messages indefinitely. In this case, message data is JSON-encoded.
