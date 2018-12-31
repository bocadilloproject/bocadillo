# Requests

Request objects in Bocadillo expose the same interface as the
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

Query parameters are available at `req.query_params`, an immutable Python
dictionary-like object.

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
For **optional** query parameters, use `.get()` instead of direct item access. Otherwise, a `KeyError` is raised if the parameter is not present.

See also: [Why dict.get(key) instead of dict[key]?](https://stackoverflow.com/questions/11041405/why-dict-getkey-instead-of-dictkey).
:::

## Body

In Bocadillo, **the response body is an awaitable**, which means it can
only be used inside **asynchronous** views.

You can retrieve it in several ways, depending on the expected encoding:

- Bytes : `await req.body()`
- Form data: `await req.form()`
- JSON: `await req.json()`
- Stream (advanced usage): `async for chunk in req.stream(): ...`

::: tip How is malformed JSON handled?
If the request body is not proper JSON, a `400 Bad Request` error response is returned.
:::