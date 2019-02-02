# Routes and URL design

The point of a web framework is to make it easy to work with HTTP requests, which means managing routes and designing URLs. This topic guide shows you how to do this in Bocadillo.

## Overview

In Bocadillo, **routes** map an URL pattern to a view function, class or method. When Bocadillo receives a request, the application router invokes the view of the matching route and returns a response.

## How are requests processed?

When an inbound HTTP requests hits your Bocadillo application, the following algorithm is used to determine which view gets executed:

1. Bocadillo runs through each URL pattern and stops at the first matching one, extracting the route parameters as well. If none can be found or any of the route parameters fails validation, an `HTTPError(404)` exception is raised.
2. Bocadillo checks that the matching route supports the requested HTTP method and raises an `HTTPError(405)` exception if it does not.
3. When this is done, Bocadillo calls the view attached to the route, converting it to an `async` function if necessary. The view is passed the following arguments:
    - An instance of [`Request`][Request].
    - An instance of [`Response`][Response].
    - Keyword arguments representing the extracted keyword arguments.
4. If no pattern matches, or if an exception is raised in the process, Bocadillo invokes an appropriate error handler (see [Route error handling](#route-error-handling) below).

## Examples

Here are a few example routes:

```python
import bocadillo

api = bocadillo.API()

@api.route('/')
async def index(req, res):
    pass

@api.route('/listings/143/')
async def get_listing_143(req, res):
    pass

@api.route('/listings/{id:d}/')
async def get_listing(req, res, id: int):
    pass
```

Note that:

- An URL pattern *should* start with a leading slash. If it doesn't, Bocadillo adds one for you (except for the catch-all pattern `{}`).
- Bocadillo honors the presence or absence of a trailing slash on the URL. It will not perform any redirection by default.
- Route parameters are defined using the F-string notation.
- Route parameters can optionally use format specifiers to perform validation and conversion. For instance, in `get_listing()`, `{id:d}` validates that `id` is an integer. By default, route parameters are extracted as strings.

Here's how a few example requests would be handled:

- A request to `/` would match the `index()` view.
- `/listings/143` would not match `get_listing_143()` because the latter's URL pattern includes a trailing slash.
- `/listings/foo/` would not match `get_listing()` because the latter's URL pattern requires that `id` be an integer.

## What the router searches against

The router searches against the requested *URL path* — which does not include the domain name nor GET or POST parameters.

## Route parameters

Route parameters allows a single URL pattern to match a variety of URLs. Their syntax is inspired by F-strings and is powered by [parse](https://pypi.org/project/parse/).

### Basic usage

A route parameter is defined with the `{param_name}` syntax. When a request is made to a matching URL, the parameter value is extracted and made available to the view.

For example, consider the following route pattern:

```python
"/say/{message}"
```

If a request is made to `/say/hello`, the view will be given a keyword argument `message` with the value `"hello"`.

You can learn more about the format syntax in the `parse` documentation: [Format Syntax](https://github.com/r1chardj0n3s/parse#format-syntax).

### Validation and conversion

Lightweight validation and conversion of route parameters can be achieved by decorating them with **format specifiers**.

This allows you to make sure the provided parameters comply with a certain format. When they don't, matching is considered to have failed.

The basic syntax is `{param_name:specifier}`. Common format specifiers include `d` for integers and `w` for alphanumerical characters.

A typical use case is using the `d` specifier to require that an `id` is an integer:

```python
from bocadillo import API

api = API()

@api.route("/items/{id:d}")
async def get_item(req, res, id: int):
    pass
```

As you can tell from the type annotation, the `id` will be given as an integer to the view instead of a string thanks to the integer specifier `d`.

You can find the full list of supported specifiers in the parse documentation: [Format Specification](https://github.com/r1chardj0n3s/parse#format-specification).

### Wildcard matching

Wildcard URL matching is made possible thanks the anonymous parameter `{}`.

This is useful to implement routes that serve as defaults when no other routes matches the requested URL.

For example, the following snippet shows how to implement a "catch-all" route.

```python
from bocadillo import API

api = API()

@api.route("{}")
async def hello(req, res):
    res.text = "Hello, world!"
```

As you can see, the value of an anonymous parameter is not passed to the view. If you need to the value, you should use a regular named route parameter.

::: warning CAUTION
- **Order matters**. If `/foo/{}` is defined before `/foo/bar`, making a request to `/foo/bar` will match the former.
- The anonymous parameter `{}` expects a **non-empty string**. This means that the pattern `/{}` will *not* match the root URL `/` because it expects a non-empty value after the leading slash.
- Wildcard routes should not be used to implement 404 pages — see the next section for how Bocadillo deals with URLs that don't match any route.
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

| View declaration | Inferred route name |
|------------------|---------------------|
| `async def do_stuff(req, res):` (or `def do_stuff(req, res):`) | `"do_stuff"` |
| `class DoStuff:` | `"do_stuff"` |

### Explicit route names

If you wish to specify an explicit name, use the `name` parameter to `@api.route()`:

```python
@api.route('/about/{who}', name='about_page')
async def about(req, res, who):
    res.html = f'<h1>About {who}</h1>'
```

### Namespacing routes

You can specify a namespace in order to group route names together:

```python
@api.route('/blog/', namespace='blog')
async def home(req, res):
    pass
```

The namespace will be prepended to the route's name (either inferred or explicit) and separated by a colon, e.g. resulting in `blog:home` for the above example.

::: tip
If you find yourself namespacing a lot of routes under a common path prefix (like above), you might benefit from writing a [recipe](../agnostic/recipes.md).
:::

## Reversing named routes

To get back the full URL path to a named route (including its optional namespace), use `api.url_for()`, passing required route parameters as keyword arguments:

```python
>>> api.url_for('about', who='them')
'/about/them'
>>> api.url_for('blog:home')
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

On function-based views, you can use the `@view()` decorator and its case-insensitive `methods` argument. If `methods` is not given or the decorator is omitted altogether, only safe HTTP methods are exposed, i.e. `GET` and `HEAD`.

```python
from bocadillo import view

@api.route("/posts/{pk}")
@view(methods=["delete"])
async def delete_blog_post(req, res, pk):
    res.status_code = 204
```

::: warning CHANGED IN v0.9.0
The `methods` argument is no longer located on `api.route()`.
:::

#### How are unsupported methods handled?

When a non-allowed HTTP method is used by a client, a `405 Not Allowed` error response is automatically returned. [Hooks] callbacks will not be called either (but request [middleware] will).

::: tip
Bocadillo implements the `HEAD` method automatically if your route supports `GET`. It is safe and systems such as URL checkers may use it to access your application without transferring the full request body.
:::

[Request]: requests.md
[Response]: responses.md
[hooks]: ./hooks.md
[middleware]: ./middleware.md
