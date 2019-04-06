# Views

Once that a route is defined with a well-designed URL pattern (see [Routing]), you'll need to write the **view** to handle the request and shape up the response.

[routing]: ./routing.md

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
- Then, we define an `async` function called `current_datetime` — this is the view function.
- Next, we grab the current date and time and build a dictionary out of it.
- Finally, we assign this dictionary to `res.media`, which results in returning a JSON response.

Note that **the view function does not return the response object**. Indeed, in Bocadillo, you shape up the response by mutating the `res` object directly, like we did here by assigning `res.media`. [Learn why in the FAQ](/faq/#why-pass-the-request-and-response-around-everywhere).

More information on working with requests and responses can be found in the [Request] and [Response] user guides.

[request]: requests.md
[response]: responses.md

## Mapping URLs to views

As you have seen above, a view is merely just a Python function. To attach it to an URL pattern, you'll need to decorate it with a route. See [Routing] for more information.

## Returning HTTP errors

Returning an HTTP error response in reaction to an exception or something that went wrong is a common pattern for which Bocadillo provides a special `HTTPError` exception.

If you raise an `HTTPError` inside a view, Bocadillo will catch it and
return an appropriate response.

As an example, consider the following route:

```python
from bocadillo import HTTPError

@app.route('/fail/{status_code}')
def fail(req, res, status_code: int):
    raise HTTPError(status_code, detail="You asked for it!")
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
You asked for it!
```

As you can see, it returned a `403 Forbidden` response — this is the HTTP error handler in action.

We will go through how `HTTPError` and error handling in general works in the next section.

## Types of views

Views can be asynchronous or synchronous, function-based or class-based.

### Asynchronous views

The recommended way to define views in Bocadillo is using the async/await syntax. This allows you to call arbitrary asynchronous Python code:

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

::: tip
It is generally more efficient to use asynchronous views than synchronous ones. This is because, when given a synchronous view, Bocadillo needs to perform a sync-to-async conversion, which might add extra overhead.
:::

### Class-based views

The previous examples were function-based views, but Bocadillo also supports class-based views. They're just regular Python classes and don't need to extend any base class.

During routing, the request gets routed to the **handler method** (or _handler_ for short) corresponding to the requested HTTP method. For example, `GET` gets mapped to `.get()`, `POST` gets mapped to `.post()`, etc.

```python
class Index:

    async def get(self, req, res):
        res.text = 'Classes, oh my!'

    # Synchronous handlers are also supported here.
    def post(self, req, res):
        res.text = 'Roger that'
```

A catch-all `.handle()` handler can be implemented to process all incoming
requests regardless of their HTTP method — resulting in other handlers being ignored.

```python
class Index:

    async def handle(self, req, res):
        res.text = 'Post it, get it, put it, delete it.'
```

::: tip NOTE
Bocadillo actually has a [`View`](/api/views.md#view) base class, but you don't need to subclass it when building class-based views. It only exists as a unique representation to which all the types of views described in this section get mapped internally.
:::
