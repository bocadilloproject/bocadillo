# Responses

Bocadillo passes the request and the response objects to each HTTP view. This means that the idiomatic way of sending a response is to mutate the `res` object directly. To learn more about this design decision, see the [FAQ](/faq.md#why-pass-the-request-and-response-around-everywhere).

## Sending content

Bocadillo has built-in support for common types of responses:

```python
res.json = {"title": "My awesome post"}  # application/json
res.text = "My awesome post"  # text/plain
res.html = "<h1>My awesome post</h1>"  # text/html
```

Setting one of the above attributes automatically sets the
appropriate `Content-Type` header (as shown in comments above).

If you need to send another content type, use `.content` and set
the `Content-Type` header yourself:

```python
res.content = "h1 { color; gold; }"
res.headers["content-type"] = "text/css"
```

## Status codes

You can set the HTTP status code of the response using `res.status_code`:

```python{8}
from bocadillo import App

app = App()

@app.route("/jobs")
class Jobs:
    async def post(self, req, res):
        res.status_code = 201
```

::: tip
Bocadillo does not provide an enum of HTTP status codes. If you prefer to
use one, you can use [Starlette's `status` module](https://github.com/encode/starlette/blob/master/starlette/status.py):

```python
from starlette import status
res.status_code = status.HTTP_201_CREATED
```

:::

## Headers

You can access and modify the headers of a response using `res.headers`. It is
a standard (but case-insensitive) Python dictionary object:

```python
res.headers["cache-control"] = "no-cache"
```

## Streaming

Similar to [request streaming](/guide/requests.md#streaming), response content can be streamed to prevent loading the full (and potentially large) response body into memory. An example use case may be streaming the results of a massive database query over the wire.

A stream response can be defined by decorating a no-argument [asynchronous generator function](https://www.python.org/dev/peps/pep-0525/#asynchronous-generators) with `@res.stream`. The generator returned by that function will be used to compose the full response. It should only yield **strings or bytes**.

For example:

```python
import asyncio

async def get_numers(k: int):
    for num in range(k):
        yield num
        # This sleep can represent a db query
        # or network call.
        await asyncio.sleep(0.01)

@app.route("/range/{n}")
async def number_range(req, res, n: int):
    @res.stream
    async def large_response():
        async for num in get_numbers(n):
            yield str(num)
```

::: warning
A stream response is not chunk-encoded by default, which means that clients will still receive the response in one piece. To send the response in chunks, see [Chunked responses](#chunked-responses).
:::

If the client disconnects and we `yield` another chunk, then the stream is stopped and no further action is taken.

If you need to react to client disconnections (e.g. to perform extra cleanup), you can pass `raise_on_disconnect=True` to `@res.stream` and handle the `ClientDisconnect` exception:

```python
from bocadillo import ClientDisconnect

...

@app.route("/range/{n}")
async def number_range(req, res, n: int):
    @res.stream(raise_on_disconnect=True)
    async def large_response():
        try
            async for num in get_numbers(n):
                yield str(num)
        except ClientDisconnect:
            print("Cleaning up numbers…")
```

## Chunked responses

The HTTP/1.1 [Transfer-Encoding] header allows to send an HTTP response in chunks.

This is useful to send large responses, or when the response's total size cannot be known until processing is finished. Plus, it allows the client to process the results as soon as possible.

This is typically combined with [response streaming](#streaming).

```python
res.chunked = True
# equivalent to:
res.headers["transfer-encoding"] = "chunked"
```

[transfer-encoding]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding

## Attachments

If you want to tell the client's browser that the response should be downloaded to a file, set `res.attachment` and the [Content-Disposition] header will be set for you.

[content-disposition]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition

```python
@app.route("/hello.txt")
async def send_hello(req, res):
    res.text = "Hi, there!"
    res.attachment = "hello.txt"
```

::: tip NOTE
`res.attachment` does **not** read any files — see [File responses](#file-responses) for this purpose.

All it does is set the `Content-Disposition` header, e.g. `attachment; filename='hello.txt'` for the example above.
:::

## File responses

::: warning REQUIREMENTS
This feature requires that you install Bocadillo with the `files` extra, e.g.

```bash
pip install bocadillo[files]
```

:::

Sometimes, the response should be populated from a file that is not a [static file](/guide/static-files.md). For example, it may have been generated or uploaded to the server.

This can be done with `res.file()`, a performant helper that will read and send a file _asynchronously_ in small chunks.

As an example, let's create a sample CSV file containing random data:

```python
import csv
from random import random

data = [{"id": i, "value": random()} for i in range(100)]

with open("random.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "value"])
    writer.writeheader()
    for item in data:
        writer.writerow(item)
```

Here's how we could populate the response with `random.csv`:

```python
@app.route("/random.csv")
async def send_csv(req, res):
    res.file("random.csv")
```

Most of the time, files sent like this are meant to be downloaded. For this reason, `res.file()` sends the file as an [attachment](#attachments) by default.

To disable this, pass `attach=False`:

```python
@app.route("/random.csv")
async def send_csv(req, res):
    # The file will be sent "inline", i.e. displayed in the browser
    # instead of triggering a download.
    res.file("random.csv", attach=False)
```
