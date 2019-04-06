# Routing

The point of a web framework is to make it easy to work with HTTP requests, which means managing routes and designing URLs. This guide shows you how to do this in Bocadillo.

## Overview

In Bocadillo, **routes** map an URL pattern to a view function, class or method. When an application receives a request, its router invokes the view for the matching route and returns a response.

## How are requests processed?

When an inbound HTTP requests hits your Bocadillo application, the following algorithm is used to determine which view gets executed:

1. Bocadillo runs through each URL pattern and stops at the first matching one, extracting the route parameters as well. If none can be found, an `HTTPError(404)` is raised.
2. Bocadillo checks that the matching route supports the requested HTTP method and raises an `HTTPError(405)` exception if it does not.
3. When this is done, Bocadillo calls the view attached to the route. If any of the route parameters fails validation, an `HTTPError(400)` exception is raised.
4. If no pattern matches, or if an exception is raised in the process, Bocadillo invokes an appropriate error handler (see [Route error handling](#route-error-handling) below).

## Examples

Here are a few example routes:

```python
from bocadillo import App

app = App()

@app.route('/')
async def index(req, res):
    pass

@app.route('/listings/143')
async def get_listing_143(req, res):
    pass

@app.route('/listings/{id}')
async def get_listing(req, res, id: int):
    pass
```

Note that:

- An URL pattern should start with a leading slash.
- Bocadillo honors the presence or absence of a trailing slash on the URL. It will not perform any redirection by default.
- Route parameters are defined using the `{param_name}` notation and passed as keyword arguments to the view.

Here's how a few example requests would be handled:

- A request to `/` would match the `index()` view.
- `/listings/143/` would not match `get_listing_143()` because the latter's URL pattern does not include a trailing slash.
- `/listings/foo` would not match `get_listing()` because its URL pattern requires `id` to be an integer.

## What the router searches against

The router searches against the requested _URL path_ — which does not include the domain name nor GET or POST parameters.

## Route parameters

Route parameters allow a single URL pattern to match a variety of URLs. Their syntax is inspired by format strings and their validation is powered by [TypeSystem].

[typesystem]: https://www.encode.io/typesystem/

### Basic usage

A route parameter is defined with the `{param_name}` syntax. When a request is made to a matching URL, the parameter value is extracted and passed to the view as a keyword argument.

Consider the following route pattern:

```python
"/say/{message}"
```

If a request is made to `/say/hello`, the view will be given a keyword argument `message` with the value `"hello"`.

### Validation and conversion

Bocadillo provides a lightweight route parameter validation mechanism based on [type annotations](https://docs.python.org/3/library/typing.html).

#### Basic usage

If the route parameter is declared on the view with a type annotation, Bocadillo automatically converts the parameter value to that type.

Consider the following example:

```python
@app.route("/items/{id}")
async def get_item(req, res, id: int):
    pass
```

By annotating `id` as an `int`, Bocadillo _automatically_ converts the extracted `id` parameter to an integer before passing it to the view. It's that simple!

#### When validation fails

If a parameter cannot be converted, a `400 Bad Request` response is returned with explicit error messages.

See what happens to the example above if we pass a non-integer `id`:

```bash
curl http://localhost:8000/items/test
```

```json
{
  "error": "400 Bad Request",
  "status": 400,
  "detail": {
    "id": "Must be a number."
  }
}
```

Very helpful for debugging! 🐛

#### TypeSystem fields

Behind the scenes, validation is powered by [TypeSystem]. This means that parameters can be annotated with any TypeSystem field:

```python
from typesystem import Integer

@app.route("/items/{quantity}")
async def get_item(req, res, quantity: Integer(minimum=0)):
    pass
```

See [TypeSystem fields](https://www.encode.io/typesystem/fields/) for the complete list of fields and their options.

#### Aliases

Annotating parameters with builtins like `int` or `bool` works thanks to the following aliases:

| Type annotation     | TypeSystem field |
| ------------------- | ---------------- |
| `int`               | `Integer`        |
| `float`             | `Float`          |
| `bool`              | `Boolean`        |
| `decimal.Decimal`   | `Decimal`        |
| `datetime.datetime` | `DateTime`       |
| `datetime.date`     | `Date`           |
| `datetime.time`     | `Time`           |

### Wildcard matching

Wildcard URL matching is made possible thanks the anonymous parameter `{}`.

This is useful to implement routes that serve as defaults when no other route matches the requested URL.

The following snippet shows how to implement a "catch-all" route.

```python
from bocadillo import App

app = App()

@app.route("{}")
async def hello(req, res):
    res.text = "Hello, world!"
```

As you can see, the value of an anonymous parameter is not passed to the view. If you need access to the value, you should use a regular named route parameter.

::: warning CAVEATS

- **Order matters**. If `/foo/{}` is defined before `/foo/bar`, making a request to `/foo/bar` will match the former.
- The anonymous parameter `{}` expects a **non-empty string**. This means that, unlike the catch-all `{}`, the pattern `/{}` will _not_ match the root URL `/` because it expects a non-empty value after the leading slash.
- Wildcard routes should not be used to implement 404 pages — read on to know how Bocadillo deals with URLs that don't match any route.

:::

## Query parameters

Similarly to route parameters, query parameters present in the URL's [querystring](https://en.wikipedia.org/wiki/Query_string) can be injected in the view. You can do so by declaring a parameter with a default value:

```python
items = list(range(10))

@app.route("/items")
async def get_items(req, res, limit: int = None):
    if limit is not None:
        items = items[:limit]
    res.media = items
```

Here's what `limit` will be for various requested URL paths:

| Requested path   | `limit`           |
| ---------------- | ----------------- |
| `/items`         | `None`            |
| `/items?limit=5` | `5` (the integer) |

[Validation and conversion features](#validation-and-conversion) available on route parameters are also available for query parameters.

::: tip NOTE
Query parameters present in the URL but not declared in the view are ignored.

You can still access them through the [Request object](./requests.md#query-parameters).
:::

## Route error handling

When Bocadillo cannot find a matching route for the requested URL, a `404 Not Found` error response is returned.

If a route was found but it did not support the requested HTTP method (e.g. `POST` or `DELETE` when only `GET` is supported), a `405 Method Not Allowed` error response is returned.

See [customizing error handling](views.md#customizing-error-handling) for how to customize this behavior.

## Naming routes

Working with absolute URLs can quickly become impractical, as changes to a route's URL pattern may require changes across the whole code base.

To overcome this, all routes are given a name which can be referenced later.

### Inferred route names

Bocadillo will assign a name to routes based on the name of their view function or class.

The inferred route name is always `snake_cased`, as shown in the table below.

| View declaration                                               | Inferred route name |
| -------------------------------------------------------------- | ------------------- |
| `async def do_stuff(req, res):` (or `def do_stuff(req, res):`) | `"do_stuff"`        |
| `class DoStuff:`                                               | `"do_stuff"`        |

### Explicit route names

If you wish to specify an explicit name, use the `name` parameter to `@app.route()`:

```python
@app.route('/about/{who}', name='about_page')
async def about(req, res, who):
    res.html = f'<h1>About {who}</h1>'
```

### Namespacing routes

You can specify a namespace in order to group route names together:

```python
@app.route('/blog/', namespace='blog')
async def home(req, res):
    pass
```

The namespace will be prepended to the route's name (either inferred or explicit) and separated by a colon, e.g. resulting in `blog:home` for the above example.

::: tip
If you find yourself namespacing a lot of routes under a common path prefix (like above), you might benefit from writing a [recipe](../agnostic/recipes.md).
:::

## Reversing named routes

To get back the full URL path to a named route (including its optional namespace), use `app.url_for()`, passing required route parameters as keyword arguments:

```python
>>> app.url_for('about', who='them')
'/about/them'
>>> app.url_for('blog:home')
'/blog/'
```

In templates, you can use the `url_for()` template global:

```html
<h1>Hello, Bocadillo!</h1>
<p>
  <a href="{{ url_for('about', who='me') }}">About me</a>
</p>
```

::: warning
Referencing a non-existing named route with `url_for()` will trigger an `HTTPError(404)` exception — **even in templates**.
:::

## Specifying HTTP methods

Which HTTP methods are exposed on a route is managed at the [view](./views.md) level.

On class-based views, HTTP methods are exposed according to the declared handlers. For example, the POST method is accepted if and only if the view defines `.post()`.

On function-based views, you can use the [`@view()`](/api/views.md#view-2) decorator and its case-insensitive `methods` argument. If `methods` is not given or the decorator is omitted altogether, only safe HTTP methods are exposed, i.e. `GET` and `HEAD`.

```python
from bocadillo import view

@app.route("/posts/{pk}")
@view(methods=["delete"])
async def delete_blog_post(req, res, pk):
    res.status_code = 204
```

### How are unsupported methods handled?

When a non-allowed HTTP method is used by a client, a `405 Not Allowed` error response is automatically returned. When this happens, [hooks] will not be called either but [HTTP middleware][middleware] will.

### Automatic implementation of `HEAD`

The `HEAD` HTTP method is used by systems such as URL checkers and web crawlers to examine a read-only resource without transferring the full request body.

As a result, Bocadillo implements the `HEAD` method automatically if your route supports `GET`.

[request]: requests.md
[response]: responses.md
[hooks]: ./hooks.md
[middleware]: ./middleware.md
