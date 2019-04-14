# Scopes

By default, a provider is recomputed on every call to the view. This is convenient when you want to provide pre-computed values — e.g. common database queries, or objects that are derived from the request — and those values are relatively cheap to compute.

However, some providers are typically expansive to setup and teardown, or could gain from being reused across requests. This is the case of providers that access the network, such as an SMTP client or, as in the [problem statement](#problem-statement), a Redis connection.

For this reason, Bocadillo providers come with two possible **scopes**:

- `request`: a new copy of the provider is computed for each HTTP request or WebSocket connection. This is the default behavior.
- `app`: the provider is reused and shared between requests.

## Example: keeping track of WebSocket clients

For example, let's build a provider for an initially empty set of clients which a WebSocket view can use to keep track of connected clients:

```python
from bocadillo import App, provider

@provider(scope="app")
def clients() -> set:
    return set()

app = App()

@app.websocket_route("/echo")
async def echo(ws, clients: set):
    clients.add(ws)
    try:
        async for message in ws:
            await ws.send(message)
    finally:
        clients.remove(ws)
```

Since `clients` is app-scoped, other routes can require it and they'll have access to the _same_ set of clients.

For example, here's an API endpoint that returns their count:

```python
@app.route("/clients-count")
async def clients_count(req, res, clients: set):
    res.json = {"count": len(clients)}
```
