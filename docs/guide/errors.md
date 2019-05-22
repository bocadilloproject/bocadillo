# Error handling

Sometimes, things go wrong. The resource the client requested does not exist, we didn't receive the data we expected, or something unexpected happens. In short: an exception is raised.

Bocadillo makes it easy to catch specific exceptions and return appropriate HTTP error responses.

## What is an error handler?

An **error handler** is an asynchronous function that gets executed when an exception occurs.

It should have the following signature: `(req, res, exc) -> None`, where `exc` is the exception that was raised.

The response `res` can be mutated just like in views in order to achieve their desired behavior (e.g. set the status code).

An error handler can also re-raise an exception to defer processing to another error handler.

For example, here is a no-op error handler which re-raises the exception it is given:

```python
async def noop(req, res, exc):
    raise exc
```

And one that silences the exception (note: probably a bad idea!):

```python
async def silence(req, res, exc):
    pass
```

Lastly, every error handler is associated to an exception class, which Bocadillo uses this to know which error handler to call when an exception is raised (see next section).

## What happens when an error is raised?

When an exception is raised within an HTTP view or middleware, the following algorithm is used:

1. We iterate over the registered exception classes until we find the one that was raised, or one that it is a subclass of (in this order).
2. The error handler found is called, and the (perhaps mutated) response is returned. If the error handler itself raises an exception, we go back to 1.
3. If no error handler was found:
   - The response is converted to an `500 Internal Server Error` response.
   - It is sent to the client and the exception is re-raised to allow server-side logging.

## Registering error handlers

To register an error handler, use the `@app.error_handler()` decorator:

```python
@app.error_handler(AttributeError)
async def on_attribute_error(req, res, exc):
    res.status = 500
    res.json = {"error": {"attribute_not_found": exc.args[0]}}
```

Note that this error handler can be simplified by re-raising an `HTTPError`:

```python
@app.error_handler(AttributeError)
async def on_attribute_error(req, res, exc):
    raise HTTPError(500, detail={"attribute_not_found": exc.args[0]})
```

For convenience, a non-decorator syntax is also available:

```python
from somelib import on_key_error

app.add_error_handler(KeyError, on_key_error)
```

## How `HTTPError` is handled

The [`HTTPError`](/api/errors.md) exception is used to return HTTP error responses within views.

Every Bocadillo application comes with an `HTTPError` error handler. The default handler returns a JSON error response.

You can register your own error handler for `HTTPError` just like for any other exception. The following handlers are available in the `bocadillo.error_handlers` module:

- `error_to_json()`: converts an exception to a JSON response (this is the default).
- `error_to_text()`: converts an exception to plain text.
- `error_to_html()`: converts an exception to an HTML response.
