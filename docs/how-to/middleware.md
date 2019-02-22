# Writing middleware

Middleware classes act as wrappers around your Bocadillo application in order to extend its behavior globally.

They come in 2 flavors: [HTTP middleware](../guides/http/middleware.md) and [ASGI middleware](../guides/agnostic/asgi-middleware.md).

## HTTP middleware

The HTTP middleware framework provides two hooks:

- `.before_dispatch()`: called before an HTTP request is dispatched (i.e. processed by the child middleware).
- `.after_dispatch()`: called after it has been dispatched.

Each hook is given the current `Request` and `Response` objects, and can alter them as necessary to achieve the desired behavior.

### Basic usage

HTTP middleware can be created by subclassing from [`Middleware`][http middleware]. A bare-bones HTTP middleware looks like this:

```python
from bocadillo import Middleware, Request, Response

class NoOpMiddleware(Middleware):

    async def before_dispatch(self, req: Request, res: Response):
        pass

    async def after_dispatch(self, req: Request, res: Response):
        pass
```

::: tip
The `.before_dispatch()` and `.after_dispatch()` can also be plain, non-`async` Python functions.
:::

### Interrupting request processing

If the `.before_dispatch()` hook returns the `Response` object, no further
processing is performed.

For example, this middleware will result in a `202 Accepted` response being
returned for _any_ request made to the application.

```python{8}
from bocadillo import Middleware, Request, Response

class Always202Middleware(Middleware):

    async def before_dispatch(self, req: Request, res: Response):
        res.status_code = 202
        return res
```

Note: returning a response in `after_dispatch` has no effect.

### Configuration and initialisation

Middleware configuaration and initialisation can be performed by overriding its `__init__()` method, which is given the following:

- `inner`: this is the inner middleware that this middleware wraps.
- `app`: this is the application instance which this middleware is being registered on.
- `**kwargs`: any keyword arguments passed to `app.add_middleware()`.

For example, here's a middleware that registers a startup [event handler](../guides/agnostic/events.md) if a flag argument was passed:

```python
from bocadillo import App, Middleware

class ExpensiveMiddleware(Middleware):

    def __init__(self, inner, app: App, warmup=False, **kwargs):
        super().__init__(inner, app, **kwargs)

        if not warmup:
            return

        @app.on("startup")
        async def perform_warmup():
            print("Warming up middleware…")
```

### Middleware from scratch

As it turns out, the `before_dispatch()` and `after_dispatch()` hooks on
`Middleware` are just helpers.

If they don't fit your needs, you can also implement the asynchronous `.__call__()` method directly. Subclassing from `Middleware` will ensure that the inner middleware, app and kwargs are available for use.

For example, here's a "no-op" middleware that forwards request processing to its inner middleware:

```python
from bocadillo import Request, Response, Middleware

class NoOpMiddleware(Middleware):

    async def __call__(self, req: Request, res: Response) -> Response:
        return await self.inner(req, res)
```

## ASGI middleware

If you need global behavior that don't belong to the world of HTTP, ASGI middleware is for you. They are lower-level middleware classes that implement the [ASGI] interface directly.

### Using the `ASGIMiddleware` base class

Similar to `Middleware`, Bocadillo provides an [`ASGIMiddleware`][asgi middleware] base class targeted at writing ASGI middleware.

Here's an example middleware that implements integration with an imaginary database library:

```python
from bocadillo import App, ASGIMiddleware
from db import Database

class DatabaseMiddleware(ASGIMiddleware):
    def __init__(self, inner, app: App, url: str):
        super().__init__(inner, app)
        self.db = Database(url)
        app.on("startup", self.db.connect)
        app.on("shutdown", self.db.disconnect)

    # ASGI implementation
    def __call__(self, scope: dict):
        # Make the db available to the request scope.
        scope["db"] = self.db
        return super().__call__(scope)
```

### Pure ASGI middleware

Bocadillo also supports "pure" ASGI middleware, i.e. middleware that only expects their `inner` middleware to be given to their constructor.

::: tip NOTE
Third-party ASGI middleware classes are typically given in this form.
:::

Note that, because it performs initialisation on the application instance, the previous `DatabaseMiddleware` cannot be rewritten as a pure ASGI middleware.

As an example, here's a pure ASGI middleware that injects a static value in the request scope:

```python
from bocadillo import App

class Inject:
    def __init__(self, inner, value: str):
        self.inner = inner
        self.value = value

    # ASGI implementation
    def __call__(self, scope: dict):
        scope["x-value"] = self.value
        return self.inner(scope)
```

Example usage:

```python
app = App()
app.add_asgi_middleware(Inject, value="foo")

@app.route("/")
async def index(req, res):
    res.text = req["x-value"]  # "foo"
```

### Caveats

Bocadillo is not able to perform error handling at the ASGI middleware level.
You must make sure you implement the ASGI protocol correctly and send
the correct ASGI events if something goes wrong.

[asgi]: https://asgi.readthedocs.io
[http middleware]: ../api/middleware.md#middleware
[asgi middleware]: ../api/middleware.md#asgimiddleware
