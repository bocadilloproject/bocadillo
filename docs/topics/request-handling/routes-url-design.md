
# Routes and URL design

The point of a web framework is to make it easy to work with HTTP requests, which means managing routes and designing URLs. This topic guide shows you how to do this in Bocadillo.

## Overview

In Bocadillo, **routes** map an URL pattern to a view function, class or method. When Bocadillo receives a request, the application router invokes the view of the matching route and returns a response.

## How are requests processed?

When an inbound HTTP requests hits your Bocadillo application, the following algorithm is used to determine which view gets executed:

1. Bocadillo runs through each URL pattern and stops at the first matching one, extracting the route parameters as well. If none can be found or any of the route parameters fails validation, an [`HTTPError(404)`][HTTPError] exception is raised.
2. Bocadillo checks that the matching route supports the requested HTTP method and raises an [`HTTPError(405)`][HTTPError] exception if it does not.
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

- Every URL pattern *must* start with a leading slash.
- Bocadillo honors the presence or absence of a trailing slash on the URL. It will not perform any redirection by default.
- Route parameters are defined using the [F-string notation].
- Route parameters can optionally use [format specifiers] to perform validation and conversion. By default, route parameters are passed as strings. For instance, in `get_listing()`, `{id:d}` validates that `id` is an integer (which `foo` obviously isn't).

Here's how a few example requests would be handled:

- A request to `/` would match the `index()` view.
- `/listings/143` would not match `get_listing_143()` because the latter's URL pattern includes a trailing slash.
- `/listings/foo/` would not match `get_listing()` because the latter's URL pattern requires that `id` be an integer.

## What the router searches against

The router searches against the requested *URL path* — which does not include the domain name nor GET or POST parameters.

For your information, [parse] is used to match the path against a known URL pattern and extract route parameters.

## Route error handling

When Bocadillo could not find a matching route for the requested URL, a `404 Not Found` error response is returned.

If a route was found but it did not supported the requested HTTP method (e.g. `POST` or `DELETE`), a `405 Method Not Allowed` error response is returned.

See [customizing error handling](./writing-views.md#customizing-error-handling) for how to customize this behavior.

## Defining named routes

Working with absolute URLs can quickly become impractical, as changes to a route's URL pattern may require changes accross the whole code base.

To overcome this, you can specify a `name` when defining a route:

```python
@api.route('/about/{who}', name='about')
async def about(req, res, who):
    res.html = f'<h1>About {who}</h1>'
```

## Reversing named routes

To get back the full URL path to a named route, use `api.url_for()`, passing required route parameters as keyword arguments:

```python
>>> api.url_for('about', who='them')
'/about/them'
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

[Request]: ../../api/requests.md
[Response]: ../../api/responses.md
[F-string notation]: https://www.python.org/dev/peps/pep-0498/
[format specifiers]: https://www.python.org/dev/peps/pep-0498/#format-specifiers
[HTTPError]: ../../api/error-handling.md
[parse]: https://pypi.org/project/parse/
