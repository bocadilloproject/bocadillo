# Requests

[`Request`](/api/request.md) objects in Bocadillo expose the same interface as the
[Starlette Request](https://www.starlette.io/requests/). Common usage is
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
req.url  # "http://localhost:8000/items?limit=10"
```

It is a string-like object that also exposes individual parts:

```python
req.url.path  # "/items"
req.url.port  # 8000
req.url.scheme  # "http"
req.url.hostname  # "127.0.0.1"
req.url.query  # "limit=10"
req.url.is_secure  # False
```

## Headers

Request headers are available at `req.headers`, an immutable, case-insensitive
Python dictionary.

```bash
curl -H "X-Framework: Bocadillo" "http://localhost:8000"
```

```python
req.headers['X-Framework']  # "Bocadillo"
req.headers['x-framework']  # "Bocadillo"
```

## Query parameters

Query parameters are available at `req.query_params`, an immutable `MultiDict`, i.e. a dictionary-like object that supports having multiple elements per key.

```bash
curl "http://localhost:8000/items?limit=10&contain=foo&contain=bar"
```

```python
req.query_params["limit"]  # "10"
req.query_params.get("notpresent")  # None
req.query_params["contains"]  # "foo" (first item)
req.query_params.getlist("contains")  # ["foo", "bar"]
```

::: tip
Query parameters can be automatically injected based on view parameters. See [Routing](./routing.md#query-parameters).
:::

## Body

In Bocadillo, **the request body is an awaitable**. You can retrieve it in several ways, depending on the expected encoding:

| Body type   | Invocation         | Return type      |
| ----------- | ------------------ | ---------------- |
| JSON        | `await req.json()` | `list` or `dict` |
| Raw         | `await req.body()` | `bytes`          |
| Form data\* | `await req.form()` | `MultiDict`^     |

Note:

- It is safe to access the request body multiple times — it is cached on the first access.
- If JSON is malformed, a `400 Bad Request` error response is returned.
- Form data contains both form data and multipart (upload) data.
- `MultiDict` is a dictionary-like object that behaves similarly to [`query_params`](#query-parameters).

## Streaming

It is possible to process the request as a stream of **bytes chunks**.

To do so, iterate (asynchronously) over the request object itself:

```python
async for chunk in req:
    # Process chunk
    text_chunk: str = chunk.decode()
    # ...
```

This is useful when the request body may be too large to be loaded in full in memory, or to implement HTTP streaming, e.g. receiving and processing an unbounded stream of data during a single HTTP session.

::: warning
The request's stream cannot be consumed more than once. If you try to do so, a `RuntimeError` will be raised.
:::
