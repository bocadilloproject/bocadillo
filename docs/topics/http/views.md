# Views

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
The view function's name is used by Bocadillo when the view is associated to the route. See [naming routes].
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
from bocadillo import HTTPError

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

::: tip
You can provide further details about what went wrong with the `detail` argument to `HTTPError`.
:::

## Customizing error handling

By default, Bocadillo sends plain text content in response to `HTTPError` exceptions raised in views.

To customize this behavior, you can override the default handler for `HTTPError`. For example, if you want to send media instead:

```python
from bocadillo import HTTPError

@api.error_handler(HTTPError)
def error_to_media(req, res, exc: HTTPError):
    res.status = exc.status_code
    res.media = {
        "error": exc.detail,
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

## Types of views

Views can be asynchronous or synchronous, function-based or class-based.

### Asynchronous views

The recommended way to define views in Bocadillo is using the async/await syntax (as in the previous example). This allows you to call arbitrary async/await
Python code:

```python
from asyncio import sleep

async def find_post_content(slug: str):
    await sleep(1)  # perhaps query a database here?
    return 'My awesome post'

async def retrieve_post(req, res, slug: str):
    res.text = await find_post_content(slug)
```

### Synchronous views

While Bocadillo is asynchronous at its core, you can also use plain Python functions to define synchronous views:

```python
def index(req, res):
    res.html = '<h1>My website</h1>'
```

**Note**: it is generally more
efficient to use asynchronous views rather than synchronous ones.
This is because, when given a synchronous view, Bocadillo needs to perform
a sync-to-async conversion, which might add extra overhead.

### Class-based views

The previous examples were function-based views, but Bocadillo also supports
class-based views.

Class-based views are regular Python classes (there is no base `View` class).
Each HTTP method gets mapped to the corresponding method on the
class. For example, `GET` gets mapped to `.get()`,
`POST` gets mapped to `.post()`, etc.

Other than that, class-based view methods are just regular views:

```python
class Index:

    async def get(self, req, res):
        res.text = 'Classes, oh my!'
       
    def post(self, req, res):
        res.text = 'Roger that'
```

A catch-all `.handle()` method can also be implemented to process all incoming
requests — resulting in other methods being ignored.

```python
class Index:

    async def handle(self, req, res):
        res.text = 'Post it, get it, put it, delete it.'
```

[Routes and URL design]: ./routes-url-design.md
[naming routes]: ./routes-url-design.md#naming-routes
[Request]: requests.md
[Response]: responses.md
