# Writing views

Once that a route is defined with a well-designed URL pattern (see [Routes and URL design]), you'll need to write the **view** to handle the request and shape up the response.

In Bocadillo, views are functions that take at least a request and a response
as arguments, and mutate those objects as necessary.

Views can be asynchronous or synchronous, function-based or class-based.

## A simple view

Here's a view that returns the current date and time in a JSON object:

```python
import datetime

async def current_datetime(req, res):
    now = datetime.datetime.now()
    res.media = {'now': now.isoformat()}
```

Let's break this code down:

- First, we import the `datetime` module.
- Then, we define an `async` function called `current_datetime` — this is the view function. A view function takes a [`Request`][Request] and a [`Response`][Response] (in this order) as its first two arguments, which are typically called `req` and `res` respectively.

::: tip
The view function's name does not matter to Bocadillo, although it is a good practice to give it a descriptive name that starts with a verb (as for any Python function).
:::

- Next, we grab the current date and time and build a dictionary out of it.
- Finally, we assign this dictionary to `res.media`, which results in returning a JSON response.

Note that **the view function does not return the response object**. Indeed, in Bocadillo, you shape up the response by mutating the `res` object directly, like we did here by assigning `res.media`.

For more information on working with requests and responses, check out our [Request] and [Response] API guides.

## Mapping URLs to views

As you have seen above, a view is merely just a Python function. To attach it to an URL pattern, you'll need to decorate it with a route. See [Routes and URL design] for more information.

## Returning errors

Returning an HTTP error response in reaction to an exception or something that went wrong is a common pattern for which Bocadillo provides a special `HTTPError` exception.

If you raise an `HTTPError` inside a view, Bocadillo will catch it and
return an appropriate response.

As an example, consider the following route:

```python
from bocadillo.exceptions import HTTPError

@api.route('/fail/{status_code:d}')
def fail(req, res, status_code: int):
    raise HTTPError(status_code)
```

Let's call `/fail/403`, to see what it returns:

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

As you can see, it returned a `403 Forbidden` response — this is `HTTPError(403)` in action.

## Customizing error handling

By default, Bocadillo sends plain text content in response to `HTTPError` exceptions raised in views.

To customize this behavior, you can override the default handler for `HTTPError`. For example, if you want to send media instead:

```python
from bocadillo.exceptions import HTTPError

@api.error_handler(HTTPError)
def error_to_media(req, res, exc: HTTPError):
    res.status = exc.status_code
    res.media = {
        "error": exc.status_phrase,
        "status": exc.status_code,
    }
```

::: tip
For convenience, the `bocadillo.error_handlers` module provides a few built-in `HTTPError` handlers, including the one above:

- `error_to_text()`: converts an exception to plain text (this is the default).
- `error_to_html()`: converts an exception to an HTML response.
- `error_to_media()`: converts an exception to a media response.
:::

More generally, you can customize error handling for *any exception* (even built-in ones like `ValueError` or `TypeError`, although this is probably not recommended) by registering an error handler as above.

A non-decorator syntax is also available:

```python
def on_attribute_error(req, res, exc: AttributeError):
    res.status = 500
    res.media = {'error': {'attribute_not_found': exc.args[0]}}

api.add_error_handler(AttributeError, on_attribute_error)
```

[Routes and URL design]: ./routes-url-design.md
[Request]: requests.md
[Response]: responses.md
