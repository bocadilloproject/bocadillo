# Routing

## Route declaration

To declare and register a new route, use the `@api.route()` decorator:

```python
@api.route('/')
async def index(req, res):
    res.text = 'Hello, Bocadillo!'
```

## Route parameters

Bocadillo allows you to specify route parameters as named template
literals in the route pattern (which uses the F-string syntax). Route parameters
are passed as additional arguments to the view:

```python
@api.route('/posts/{slug}')
async def retrieve_post(req, res, slug: str):
    res.text = 'My awesome post'
```

## Route parameter validation

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

You can specify a name for a route by passing `name` to `@api.route()`:

```python
@api.route('/about/{who}', name='about')
async def about(req, res, who):
    res.html = f'<h1>About {who}</h1>'
```

In code, you can get the full URL path to a route using `api.url_for()`:

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

By default, a route accepts all HTTP methods. On function-based views,
you can use the `methods` argument to `@api.route()` to specify the set of
HTTP methods being exposed:

```python
@api.route('/', methods=['get'])
async def index(req, res):
    res.text = "Come GET me, bro"
```

**Note**: the `methods` argument is ignored on class-based views.
You should instead decide which methods are implemented on the class to control
the exposition of HTTP methods.

## Route hooks

Hooks allows you to call arbitrary code before and after a view is executed. They materialize as the `api.before()` and `api.after()` decorators.

```python
from bocadillo.exceptions import HTTPError

def validate_has_my_header(req, res, view, params):
    if 'x-my-header' not in req.headers:
        raise HTTPError(400)

@api.before(validate_has_my_header)
@api.route('/foo')
async def foo(req, res):
    pass
```

::: warning
Always position `@api.before()` or `@api.after()` above the `@api.route()` decorator.
:::

As a first level of reusability, you can pass extra arguments for the hook function directly to `before()` and `after()`:

```python
def validate_has_header(req, res, view, params, header):
    if header not in req.headers:
        raise HTTPError(400)

@api.before(validate_has_header, 'x-my-header')
@api.route('/foo')
async def foo(req, res):
    pass
```

A hook function only just needs to be a callable, so it can be a class that implements `__call__()` too. This is very convenient for building reusable hook functions:

```python
class RequestHasHeader:
    
    def __init__(self, header):
        self.header = header
       
    def __call__(self, req, res, view, params):
        if self.header not in req.headers:
            raise HTTPError(400)

@api.before(RequestHasHeader('x-my-header'))
@api.route('/foo')
async def foo(req, res):
    pass
```

You can, of course, use before and after hooks on class-based views too:

```python
@api.route('/')
class Foo:

    @api.before(RequestHasHeader('x-my-header'))
    async def get(self, req, res):
        pass
```
