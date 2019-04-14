# WebSocket routing

## How WebSocket requests are processed

When a client makes a request to your server with the `ws://` or `wss://` scheme, the following happens:

1. The client and the frontend web server perform a handshake to agree to [upgrade the protocol][upgrade] to WebSocket. This is not handled by Bocadillo directly.
2. The upgraded request is routed to Bocadillo and a [`WebSocket`] object is created out of it.
3. Bocadillo tries to match the WebSocket's URL path against a registered WebSocket route. If none is found, the connection is closed with a 403 close code. This is compliant with the [ASGI specification][asgi close].
4. Bocadillo calls the view attached to the route that matched. It must be an asynchronous function accepting the following parameters:
   - An instance of `WebSocket`.
   - Keyword arguments representing the extracted route parameters.
5. If an exception is raised in the process, the connection is closed by following the procedure described in [Error handling].

[upgrade]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Protocol_upgrade_mechanism
[`websocket`]: /api/websockets.md#websocket
[asgi close]: https://asgi.readthedocs.io/en/latest/specs/www.html#close
[error handling]: ./error-handling.md

## Comparison with HTTP routing

The routing of WebSocket connection requests resembles that of HTTP request (as described in [Routes and URL design][http-routes]) in the following way:

[http-routes]: ../http/routing.md

- The same URL path matching algorithm is used.
- When a route is found, the corresponding WebSocket view is called and route parameters are passed as extra keyword arguments.

However, there are also a few differences:

- Requests that do not match a known route are turned down with a 403 close code, instead of returning a 404 HTTP error response.
- There is no support for WebSocket redirection.
- There is, of course, no HTTP method checks because WebSockets do not use them.

## Inspecting the connection request

The [`WebSocket`] object itself holds information about the incoming connection request.

### URL

The full URL of the connection request is available as `ws.url`. It is a `str`-like object that also exposes individual parts.

Example URL parts when a client connects to `ws://localhost:8000/chatroom?add=sub`:

```python
ws.url  # "ws://127.0.0.1:8000/chatroom?add=sub"
ws.url.path  # "/chatroom"
ws.url.port  # 8000
ws.url.scheme  # "ws"
ws.url.hostname  # "127.0.0.1"
ws.url.query  # "add=sub"
ws.url.is_secure  # False
```

### Headers

WebSocket headers are available at `ws.headers`, an immutable, case-insensitive Python dictionary.

```python
ws.headers["sec-websocket-version"]  # "13"
```

### Query parameters

Query parameters are available at `ws.query_params`, an immutable Python
dictionary-like object.

Example if a client connects to `ws://localhost:8000/chatroom?add=1&sub=2&sub=3`:

```python
ws.query_params["add"]  # "1"
ws.query_params["sub"]  # "2"  (first item)
ws.query_params.getlist("sub")  # ["2", "3"]
```
