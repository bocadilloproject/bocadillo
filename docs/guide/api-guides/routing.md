# Routing

## Declaring a route

To declare and register a new route, use the `@api.route()` decorator:

```python
@api.route('/')
async def index(req, res):
    res.text = 'Hello, Bocadillo!'
```

## Parameters

Bocadillo allows you to specify route parameters as named template
literals in the route pattern (which uses the F-string syntax). Route parameters
are passed as additional arguments to the view:

```python
@api.route('/posts/{slug}')
async def retrieve_post(req, res, slug: str):
    res.text = 'My awesome post'
```

## Validating route parameters

You can leverage [F-string specifiers](https://docs.python.org/3/library/string.html#format-specification-mini-language) to add lightweight validation
to routes:

```python
# Only decimal integer values for `x` will be accepted
@api.route('/negation/{x:d}')
async def negate(req, res, x: int):
    res.media = {'result': -x}
```

```bash
curl "http://localhost:8000/negation/abc"
```

```http
HTTP/1.1 404 Not Found
server: uvicorn
date: Wed, 07 Nov 2018 20:24:31 GMT
content-type: text/plain
transfer-encoding: chunked

Not Found
```

## Named routes

You can specify a name for a route by passing `name` to `@api.route()`, which is useful to prevent hard-coding URLs in your codebase:

```python
@api.route('/about/{who}', name='about')
async def about(req, res, who):
    res.html = f'<h1>About {who}</h1>'
```

You can then get the full URL path to a route using `api.url_for()`:

```python
>>> api.url_for('about', who='them')
'/about/them'
```

In templates, you can use the `url_for()` global:

```jinja2
<h1>Hello, Bocadillo!</h1>
<p>
    <a href="{{ url_for('about', who='me') }}">About me</a>
</p>
```

**Note**: referencing to a non-existing named route with `url_for()` will return a 404 error page.

## Specifying HTTP methods (function-based views only)

By default, a route exposes the following HTTP methods: GET, HEAD, POST, PUT, DELETE, OPTIONS, PATCH.

On function-based views,
you can use the `methods` argument to `@api.route()` to specify the set of
HTTP methods being exposed:

```python
@api.route('/', methods=['get'])
async def index(req, res):
    res.text = "Come GET me, bro"
```

When a non-allowed HTTP method is used by a client, a `405 Not Allowed` error response is automatically returned. Callbacks such as [hooks](#hooks) and [middleware](./middleware.md) callbacks will not be called either.

::: tip
The `methods` argument is ignored on class-based views. You should instead decide which methods are implemented on the class to control
the exposition of HTTP methods.
:::

## Hooks

Hooks allow you to call arbitrary code before and after a view is executed. They materialize as the `@api.before()` and `@api.after()` decorators.
 
 These decorators take a **hook function**, which is a synchronous or asynchronous function with the following signature: `(req: Request, res: Response, params: dict) -> None`.

Here's an example:

```python
from asyncio import sleep
from bocadillo.exceptions import HTTPError

def validate_has_my_header(req, res, params):
    if 'x-my-header' not in req.headers:
        raise HTTPError(400)

async def validate_response_is_json(req, res, params):
    await sleep(1)  # for the sake of example
    assert res.headers['content-type'] == 'application/json'

@api.before(validate_has_my_header)
@api.after(validate_response_is_json)
@api.route('/foo')
async def foo(req, res):
    res.media = {'message': 'valid!'}
```

::: warning
Due to the way hooks are implemented, you must always put `@api.before()` and `@api.after()` **above** the `@api.route()` decorator.
:::

As a first level of reusability, you can pass extra arguments for the hook function directly to `@api.before()` and `@api.after()`:

```python
def validate_has_header(req, res, params, header):
    if header not in req.headers:
        raise HTTPError(400)

@api.before(validate_has_header, 'x-my-header')
@api.route('/foo')
async def foo(req, res):
    pass
```

A hook function only just needs to be a callable, so it can be a class that implements `__call__()` too. This is another convenient way of building reusable hooks functions:

```python
class RequestHasHeader:
    
    def __init__(self, header):
        self.header = header
       
    def __call__(self, req, res, params):
        if self.header not in req.headers:
            raise HTTPError(400)

@api.before(RequestHasHeader('x-my-header'))
@api.route('/foo')
async def foo(req, res):
    pass
```

You can also use hooks on class-based views:

```python
def show_content_type(req, res, view, params):
    print(res.headers['content-type'])

@api.after(show_content_type)
@api.route('/')
class Foo:

    @api.before(RequestHasHeader('x-my-header'))
    async def get(self, req, res):
        res.media = {'header': req.headers['x-my-header']}
```
