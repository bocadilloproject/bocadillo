# Requests

Request objects in Bocadillo expose the same interface as the
[Starlette Request](https://www.starlette.io/requests/) (our `Request` class is in fact a subclass of Starlette's). Common usage is
documented here.

## Method

The HTTP method of the request is available at `req.method`.

```bash
curl -X POST "http://localhost:8000"
```

```python
req.method  # 'POST'
```

## URL

The full URL of the request is available as `req.url`:

```bash
curl "http://localhost:8000/foo/bar?add=sub"
```

```python
req.url  # 'http://localhost:8000/foo/bar?add=sub'
```

It is in fact a string-like object that also exposes individual parts:

```python
req.url.path  # '/foo/bar'
req.url.port  # 8000
req.url.scheme  # 'http'
req.url.hostname  # '127.0.0.1'
req.url.query  # 'add=sub'
req.url.is_secure  # False
```

## Headers

Request headers are available at `req.headers`, an immutable, case-insensitive
Python dictionary.

```bash
curl -H 'X-App: Bocadillo' "http://localhost:8000"
```

```python
req.headers['x-app']  # 'Bocadillo'
req.headers['X-App']  # 'Bocadillo'
```

## Query parameters

Query parameters are available at `req.query_params`, an immutable `MultiDict`, i.e. a dictionary-like object that supports having multiple elements per key.

```bash
curl "http://localhost:8000?add=1&sub=2&sub=3"
```

```python
>>> req.query_params["add"]
"1"
>>> req.query_params.get("mul")
None  # not present
>>>
req.query_params["sub"]
"2"  # first item
>>> req.query_params.getlist("sub")
["2", "3"]
```

::: tip
For convenience, query parameters can be automatically injected based on view parameters. See [Routing](./routing.md#query-parameters).
:::

## Body

In Bocadillo, **the request body is an awaitable**, which means it can
only be used inside **asynchronous** views.

You can retrieve it in several ways, depending on the expected encoding:

| Body type | Invocation         | Return type      |
| --------- | ------------------ | ---------------- |
| Raw       | `await req.body()` | `bytes`          |
| Form data | `await req.form()` | `MultiDict`\*    |
| JSON      | `await req.json()` | `list` or `dict` |

\*This is a dictionary-like object that behaves like [`query_params`](#query-parameters). It contains both form data and multipart (upload) data.

::: tip How is malformed JSON handled?
If the request body is not proper JSON, a `400 Bad Request` error response is returned.
:::

## Streaming

It is possible to process the request as a stream of **bytes chunks**.

To do so, iterate (asynchronously) over the request object itself:

```python
async for chunk in req:
    # Process chunk
    text_chunk: str = chunk.decode()
    # ...
```

This is useful when the request body may be too large to be fully loaded in memory, or to implement HTTP streaming, e.g. receiving and processing an unbounded stream of data during a single HTTP session.

::: warning
The request's stream cannot be consumed more than once. If you try to do so, a `RuntimeError` will be raised.
:::
