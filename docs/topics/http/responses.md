# Responses

Bocadillo passes the request and the response object to each view, much like
Falcon does.
To send a response, the idiomatic process is to mutate the `res` object directly.

## Sending content

Bocadillo has built-in support for common types of responses:

```python
res.text = 'My awesome post'  # text/plain
res.html = '<h1>My awesome post</h1>'  # text/html
res.media = {'title': 'My awesome post'}  # application/json
```

Setting a response type attribute automatically sets the
appropriate `Content-Type`, as depicted above.

::: tip
The `res.media` attribute serializes values based on the `media_type` configured on the API, which is `application/json` by default. Refer to [Media] for more information.
:::

If you need to send another content type, use `.content` and set
the `Content-Type` header yourself:

```python
res.content = 'h1 { color; gold; }'
res.headers['Content-Type'] = 'text/css'
```

## Status codes

You can set the numeric status code on the response using `res.status_code`:

```python
@api.route('/jobs', methods=['post'])
async def create_job(req, res):
    res.status_code = 201
```

::: tip
Bocadillo does not provide an enum of HTTP status codes. If you prefer to
use one, you'd be safe enough going for `HTTPStatus`, located in the standard
library's `http` module.

```python
from http import HTTPStatus
res.status_code = HTTPStatus.CREATED.value
```
:::

## Headers

You can access and modify a response's headers using `res.headers`, which is
a standard Python dictionary object:

```python
res.headers['Cache-Control'] = 'no-cache'
```

## Streaming

Similar to [request streaming](./requests.md#streaming), response content can be streamed to prevent loading a full (potentially large) response body in memory. An example use case may be sending results of a massive database query.

A stream response can be defined by decorating a no-argument [asynchronous generator function][async generators] with `@res.stream`. The generator returned by that function will be used to compose the full response. It should only yield **strings or bytes** (i.e. [media][Media] streaming is not supported).

```python{7,8,9,10}
from bocadillo import API

api = API()

@api.route("/range/{n}")
async def number_range(req, res, n):
    @res.stream
    async def large_response():
        for num in range(n):
            yield str(num)
```

::: tip
By default, a stream response is also sent [in chunks](#chunked-responses) to allow clients to consume it as a stream too. You can disable this behavior with `@res.stream(chunked=False)`.
:::

::: tip
All attributes of the `Response` object — including [res.background](./background-tasks.md) but excluding [content attributes](#sending-content) — can be used along with a stream response.
:::

## Chunked responses

The HTTP/1.1 [Transfer-Encoding] header allows to send an HTTP response in chunks.

This is useful to send large responses in pieces, or when the response's total size cannot be known until processing is finished. Plus, it allows the client to process the results as soon as possible.

This is typically combined with [response streaming](#streaming).

```python
res.chunked = True
# equivalent to:
res.headers["transfer-encoding"] = "chunked"
```

[Transfer-Encoding]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding

[async generators]: https://www.python.org/dev/peps/pep-0525/#asynchronous-generators
[Media]: media.md
