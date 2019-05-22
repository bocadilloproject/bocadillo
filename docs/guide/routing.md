# Routing

Bocadillo makes it very easy to handle HTTP requests, i.e. mapping URL patterns to views.

## Overview

In Bocadillo, **routes** map an **URL pattern** to a **view**, which can be a function or a class. When an application receives a request, its router invokes the view for the matching route which generates the response.

## How are requests processed?

When an inbound HTTP requests hits your Bocadillo application, the following algorithm is used to determine which view gets executed:

1. Bocadillo runs through each URL pattern and stops at the first matching one, extracting the raw route parameters as well. If none can be found, an `HTTPError(404)` is raised.
2. Bocadillo checks that the matching route supports the requested HTTP method, and raises an `HTTPError(405)` exception if it does not.
3. When this is done, Bocadillo calls the view attached to the route. If any of the route parameters fails validation, an `HTTPError(400)` exception is raised.
4. If no pattern matches, or if an exception is raised in the process, Bocadillo invokes an appropriate error handler (see [Route error handling](#route-error-handling) below).

The router searches against the requested **URL path**. This does not include the domain name nor query parameters.

## Routes examples

Here are a few example routes:

```python
from bocadillo import App

app = App()

@app.route("/")
async def home(req, res):
    pass

@app.route("/items/42")
async def get_item_42(req, res):
    pass

@app.route("/items/{pk}")
async def get_items(req, res, pk: int):
    pass
```

Note that:

- An URL pattern should start with a leading slash.
- Bocadillo honors the presence or absence of a trailing slash on the URL. It will not perform any redirection by default.
- Route parameters are passed as keyword arguments to the view.

Here's how a few example requests would be handled:

| Requested URL path | Matched route   | Reason                                                             |
| ------------------ | --------------- | ------------------------------------------------------------------ |
| `/`                | `home()`        | Only matching route.                                               |
| `/items/13`        | `get_items()`   | Only matching route.                                               |
| `/items/42`        | `get_item_42()` | First route to match.                                              |
| `/items/42/`       | None            | URL pattern for `get_item_42()` does not include a trailing slash. |
| `/items/foo`       | None            | URL pattern for `get_items()` requires `pk` to be an integer.      |

## Function-based views

A route maps an URL pattern to a **view**. A view consists in an **asynchronous function** that takes as input the request (`req` by convention), the response (`res` by convention), and any keyword arguments obtained from route or query parameters (more on this in the next sections).

We've already used function-based views in the examples above. One thing to remember is that **views must be asynchronous**, i.e. defined with the `async def` syntax. This allows you to call arbitrary async code in views, e.g.:

```python
import asyncio

async def find_post_content(slug: str) -> str:
    await asyncio.sleep(1)  # perhaps query a database here?
    return "My awesome post"

@app.route("/post/{slug}")
async def retrieve_post(req, res, slug: str):
    res.text = await find_post_content(slug)
```

## Class-based views

Bocadillo also supports **class-based views**. Incoming requests get dispatched to the method on the class named after the requested HTTP method. For example, `GET` is dispatched to `.get()`, `POST` is dispatched to `.post()`, etc. Thanks to this mechanism, there is no base class — just write regular Python classes!

Here's an example route using class-based view:

```python
@app.route("/")
class Home:
    async def get(self, req, res):
        res.text = 'Classes, oh my!'

    async def post(self, req, res):
        res.text = 'Roger that'
```

If the `.handle()` method is implemented, all incoming requests are dispatched to it regardless of their HTTP method:

```python
@app.route("/")
class Home:
    async def handle(self, req, res):
        res.text = 'Post it, get it, put it, delete it.'
```

::: tip IMPLEMENTATION DETAILS
Bocadillo actually has a [`View`](/api/views.md#view) base class, but you don't need to subclass it when building class-based views. It only exists as a unique representation to which function- and class-based views are internally converted to.
:::

## HTTP methods

Which HTTP methods are exposed on a route depends on the view function or class.

On class-based views, HTTP methods are exposed based on the class' methods. For example, the POST method is accepted if and only if the view implements `.post()`.

On function-based views, you can use the [`@view()`](/api/views.md#view-2) decorator and its case-insensitive `methods` argument:

```python
from bocadillo import view

@app.route("/items")
@view(methods=["post"])
async def create_item(req, res):
    # ...
    res.status_code = 201
```

If `methods` is not given, or the decorator is omitted altogether, only safe HTTP methods are exposed, i.e. `GET` and `HEAD`.

When a non-allowed HTTP method is requested by a client, a `405 Not Allowed` error response is automatically returned.

::: tip
Bocadillo automatically implements the `HEAD` method if your route supports `GET`.

We do this to allow URL checkers and web crawlers to examine endpoints without transferring the full request body.
:::

## Route parameters

Route parameters allow a single URL pattern to match a variety of URLs.

A route parameter is defined with the `{param_name}` syntax. When a request is made to a matching URL, the parameter value is extracted and passed to the view as a keyword argument.

Consider the following route:

```python
@app.route("/say/{message}")
async def say(req, res, message):
    res.text = f"You said: '{message}'"
```

If a request is made to `/say/hello`, the view will be given a keyword argument `message` with the value `"hello"`:

```bash
curl "http://localhost:8000/say/hello"
```

```http
HTTP/1.1 200 OK
date: Sat, 18 May 2019 09:35:51 GMT
server: uvicorn
content-type: text/plain
content-length: 5

You said: 'hello'
```

## Validation and conversion

Bocadillo provides a lightweight **route parameter validation mechanism** based on [type annotations](https://docs.python.org/3/library/typing.html) and the [TypeSystem] data validation library.

[typesystem]: https://www.encode.io/typesystem/

**How it works**: if the route parameter declared on the view has a type annotation, Bocadillo automatically converts the parameter value to that type. If it is not annotated, the value is passed as a string.

For example:

```python{2}
@app.route("/items/{pk}")
async def get_item(req, res, pk: int):
    pass
```

By annotating `pk` as an `int`, Bocadillo _automatically_ converts the extracted `pk` parameter to an integer before passing it to the view. It's that simple!

If a parameter cannot be converted, a `400 Bad Request` response is returned with an explicit error message. For example:

```bash
curl "http://localhost:8000/items/notanumber"
```

```json
{
  "error": "400 Bad Request",
  "status": 400,
  "detail": {
    "pk": "Must be a number."
  }
}
```

You can also annotate parameters with a **TypeSystem field** directly:

```python
from typesystem import Integer

@app.route("/items/{quantity}")
async def get_item(req, res, quantity: Integer(minimum=0)):
    pass
```

As it turns out, annotating parameters with builtins such as `int` or `bool` only works because Bocadillo provides **aliases to TypeSystem fields**. Here's the full list of available aliases:

| Type annotation     | TypeSystem field |
| ------------------- | ---------------- |
| `int`               | `Integer()`      |
| `float`             | `Float()`        |
| `bool`              | `Boolean()`      |
| `decimal.Decimal`   | `Decimal()`      |
| `datetime.datetime` | `DateTime()`     |
| `datetime.date`     | `Date()`         |
| `datetime.time`     | `Time()`         |

See also [TypeSystem fields](https://www.encode.io/typesystem/fields/) for the complete list of fields and their options.

## Query parameters

Similarly to route parameters, query parameters present in the URL's [querystring](https://en.wikipedia.org/wiki/Query_string) can be validated and injected into the view.

You can do so by declaring a parameter with a default value, and optionally type-annotating it:

```python
ITEMS = list(range(10))

@app.route("/items")
async def get_items(req, res, limit: int = None):
    res.json = ITEMS[:limit] if limit is not None else ITEMS[:]
```

Here's what the value of `limit` will be for various requested URL paths:

| Requested path   | `limit`           |
| ---------------- | ----------------- |
| `/items`         | `None`            |
| `/items?limit=5` | `5` (the integer) |

Validation works as expected: requesting `/items?limit=notanumber` will result in a `400 Bad Request` error response.

```json
{
  "error": "400 Bad Request",
  "status": 400,
  "detail": {
    "limit": "Must be a number."
  }
}
```

::: tip NOTE
Raw query parameters can be accessed through the [Request object](./requests.md#query-parameters).
:::

## Wildcard matching

Wildcard URL matching is made possible thanks the anonymous parameter `{}`. This is useful to implement routes that serve as defaults when no other routes match the requested URL path.

For example, here's how to implement a "catch-all" route:

```python
@app.route("{}")
async def hello(req, res):
    res.text = "Hello, world!"
```

As you can see, the value of an anonymous parameter is not passed to the view. If you need access to the value, you should use a regular named route parameter.

::: warning CAVEATS

- **Order matters**. If `/foo/{}` is defined before `/foo/bar`, making a request to `/foo/bar` will match `/foo/{}`. As a rule of thumb, define wildcard routes last.
- The anonymous parameter `{}` expects a **non-empty string**. This means that, unlike the catch-all `{}` (which is actually a special case), the pattern `/{}` will _not_ match the root URL `/` because it expects a non-empty value after the leading slash.
- Wildcard routes should not be used to implement 404 pages — Bocadillo already returns those for you.

:::

## Redirecting

Inside a view, you can redirect to another URL by raising a `Redirect` exception. The given URL can be internal (a path relative to the server's host) or external (an absolute URL).

```python
from bocadillo import Redirect

@app.route("/")
async def index(req, res):
    raise Redirect("/home")
    # or, equivalently:
    raise Redirect("http://localhost:8000/home")
```

Redirections are temporary (302) by default. To return a permanent (301) redirection, pass `permanent=True`:

```python
raise Redirect("/home", permanent=True)
```
