# Response
```python
Response(self, request: starlette.requests.Request, media: bocadillo.media.Media)
```
The response builder, passed to HTTP views and typically named `res`.

At the lower-level, `Response` behaves like an ASGI application instance:
it is a callable and accepts `receive` and `send` as defined in the [ASGI
spec](https://asgi.readthedocs.io/en/latest/specs/main.html#applications).

[media]: ../guides/http/media.md

__Attributes__

- `content (bytes or str)`: the raw response content.
- `status_code (int)`: the HTTP status code. If not set, defaults to `200`.
- `headers (dict)`:
    a case-insensitive dictionary of HTTP headers.
    If not set, `content-type` header is set to `text/plain`.
- `request (Request)`: the currently processed request.
- `chunked (bool)`: sets the `transfer-encoding` header to `chunked`.

**Content setters**

These write-only properties set the response's `content`.

- `text (str)`: uses the `text/plain` content type.
- `html (str)`: uses the `text/html` content type.
- `media (any)`: uses the configured [media] handler.


## background
```python
Response.background(self, func: Callable[..., Coroutine], *args, **kwargs) -> Callable[..., Coroutine]
```
Register a coroutine function to be executed in the background.

This can be used either as a decorator or a regular function.

__Parameters__

- __func (callable)__:
    A coroutine function.
- __*args, **kwargs__:
    Any positional and keyword arguments to pass to `func` when
    executing it.

## stream
```python
Response.stream(self, func: Callable[[], AsyncIterable[Union[str, bytes]]]) -> Callable[[], AsyncIterable[Union[str, bytes]]]
```
Stream the response.

Should be used to decorate a no-argument asynchronous generator
function.

