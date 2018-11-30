# Handling HTTP requests

The point of a web framework is to make it easy to work with HTTP requests. This topic guide shows you how to do it in Bocadillo.

## Routes and URL design

### Overview

In Bocadillo, **routes** map an URL pattern to a view function, class or method. When Bocadillo receives a request, the application router invokes the view of the matching route and returns a response.

### How requests are processed

When an inbound HTTP requests hits your Bocadillo application, the following algorithm is used to determine which view gets executed:

1. Bocadillo runs through each URL pattern and stops at the first matching one, extracting the route parameters as well. If none can be found or any of the route parameters fails validation, an `HTTPError(404)` exception is raised.
2. Bocadillo checks that the matching route supports the requested HTTP method and raises an `HTTPError(405)` exception if it does not.
3. When this is done, Bocadillo calls the view attached to the route, converting it to an `async` function is necessary. The view is passed the following arguments:
    - An instance of [Request].
    - An instance of [Response].
    - Keyword arguments made up from route parameters, with the same name than that defined in the URL pattern.
4. If no pattern matches, or if an exception is raised in the process, Bocadillo invokes an appropriate error handler. See [Error handling](#error-handling) below.

### Examples

Here are a few example routes and views:

```python
import bocadillo

api = bocadillo.API()

@api.route('/')
async def index(req, res):
    pass

@api.route('/listings/143/')
async def get_listing_143(req, res):
    pass

@api.route('/blog-posts/{slug}')
async def get_blog_post(req, res, slug: str):
    pass

@api.route('/listings/{id:d}')
async def get_listing(req, res, id: int):
    pass

@api.route('/listings', methods=['post'])
async def create_listing(req, res):
    pass
```

Note that:

- Every URL pattern *must* start with a leading slash.
- Bocadillo fulfills the presence or absence of a trailing slash on the URL, and will not perform any redirection by default.
- Route parameters are defined using the [F-string notation].
- Route parameters can optionally use a [format specifier] to perform validation and conversion. If no specifier is used, the route parameter will be an `str`. In `get_listing()`, `{id:d}` ensures `id` is a valid integer.

Example requests:

- A request to `/` would match the `index()` view.
- `/listings/143` would not match `get_listing_143()` because the latter's URL pattern includes a trailing slash.
- `/listings/foo` would not `get_listing()` because the latter's URL pattern requires that `id` be a valid integer. 
- A request to ``

### Parameter validation and conversion

### What the router searches against

### Error handling

When Bocadillo cannot find a matching route for the requested URL, a 404 error response is returned by invoking `HTTPError(404)`.

See [customizing error responses](#customizing-error-responses) for more details.

### Defining named routes

### Reversing named routes

## Writing views

```python
import bocadillo

api = bocadillo.API()

listings = [
    {'id': 143, 'title': 'Software Engineer'},
]

def find_listing(id: int):
    for listing in listings:
        if listing['id'] == id:
            return listing
    return None


@api.route('/')
async def index(req, res):
    res.html = '<h1>Hello, world!</h1>'

@api.route('/listings/143')
async def get_listing_143(req, res):
    res.media = find_listing(143)

@api.route('/blog-posts/{slug}')
async def get_blog_post(req, res, slug: str):
    res.media = f'A blog post about {slug}'

@api.route('/listings/{id:d}')
async def get_listing(req, res, id: int):
    res.media = find_listing(id)

@api.route('/listings', methods=['post'])
async def create_listing(req, res):
    listing = await req.json()
    listings.append(listing)
    res.status_code = 201
```

### A simple view

### Returning errors

### The `HTTPError` exception

### Customizing error responses

### 

Taking inspiration from Falcon, Bocadillo passes the `Request` and `Response` object directly to the view. The former can be used to inspect the current HTTP request while the latter is designed to be mutated in order to build the intended HTTP response.

In practice, this means that every view is given an instance of the `Request` and `Response` class as its first and second arguments respectively (second and third for methods of [class-based views]).

Here's how it looks in the code:

```python
async def index(req, res):
    print('Crafting a response for request at', req.url)
    res.html = '<h1>Hello, world!</h1>'
```

For the complete list of attributes, options and methods on the  `req` and `res` objects, see our [Request] and [Response] API guides.


## Forms

## File uploads

[Request]: ../api-guides/requests.md
[Response]: ../api-guides/responses.md
[class-based views]: ../api-guides/views.md#class-based-views
[F-string notation]: https://www.python.org/dev/peps/pep-0498/
