# Error handling

## Returning error responses

If you raise an `HTTPError` inside a view, Bocadillo will catch it and
return an appropriate response:

```python
from bocadillo.exceptions import HTTPError

@api.route('/fail/{status_code:d}')
def fail(req, res, status_code: int):
    raise HTTPError(status_code)
```

```bash
curl -SD - "http://localhost:8000/fail/403"
```

```http
HTTP/1.1 403 Forbidden
server: uvicorn
date: Wed, 07 Nov 2018 19:55:56 GMT
content-type: text/plain
transfer-encoding: chunked

Forbidden
```

## Customizing error handling

You can customize error handling by registering your own error handlers.
This can be done using the `@api.error_handler()` decorator:

```python
from bocadillo.exceptions import HTTPError

@api.error_handler(HTTPError)
def on_key_error(req, res, exc: HTTPError):
    res.status = exc.status_code
    res.media = {
        'status_code': exc.status_code,
        'detail': exc.status_phrase,
    }
```

For convenience, a non-decorator syntax is also available:

```python
def on_attribute_error(req, res, exc: AttributeError):
    res.status = 500
    res.media = {'error': {'attribute_not_found': exc.args[0]}}

api.add_error_handler(AttributeError, on_attribute_error)
```
