# Writing middleware

Middleware classes act as wrappers around your Bocadillo application in order to extend its behavior globally.

They come in 2 flavors: [HTTP middleware](../guides/http/middleware.md) and [ASGI middleware](../guides/agnostic/asgi-middleware.md).

## HTTP middleware

The HTTP middleware framework provides two hooks:

- `.before_dispatch()`: called before an HTTP request is dispatched (i.e. processed by the child middleware).
- `.after_dispatch()`: called after it has been dispatched.

Each hook is given the current `Request` and `Response` objects, and can alter them as necessary to achieve the desired behavior.

### Basic usage

HTTP middleware can be created by subclassing from [`Middleware`](/api/middleware.md#middleware). A bare-bones HTTP middleware looks like this:

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

### Configuration and initialization

Middleware configuaration and initialization can be performed by overriding its `__init__()` method, which is given the following:

- `inner`: this is the inner middleware that this middleware wraps.
- `app`: this is the application instance which this middleware is being registered on.
- `**kwargs`: any keyword arguments passed to `app.add_middleware()`.

For example, here's a middleware that registers a startup [event handler](../guides/architecture/events.md) if a flag argument was passed:

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

If you need global behavior that does not only apply to HTTP, you can go bare-metal and use ASGI middleware classes. They are lower-level middleware classes that implement the [ASGI] interface directly.

Beside the inner ASGI `app`, the middleware's `__init__()` method can accept extra parameters for configuration purposes. Users can pass values for those arguments when calling `.add_asgi_middleware()` on the application (see the [ASGI Middleware guide](/guides/agnostic/asgi-middleware.md)).

::: tip CHANGED IN 0.15
There is no `ASGIMiddleware` base class anymore.
:::

As an example, here is an ASGI middleware class that injects a static value into the ASGI scope:

```python
from bocadillo import App

class Inject:
    def __init__(self, app, value: str):
        self.app = app
        self.value = value

    # ASGI implementation
    async def __call__(self, scope, receive, send):
        scope["x-value"] = self.value
        await self.app(scope, receive, send)
```

::: warning
Here, `app` represents the **inner ASGI application** (which is very likely to be another middleware). Note that it will _not_ be the Bocadillo `App` object.
:::

Example usage:

```python
app.add_asgi_middleware(Inject, value="foo")

@app.route("/value")
async def index(req, res):
    res.text = req["x-value"]  # "foo"
```

### Caveats

Bocadillo is not able to perform error handling at the ASGI middleware level.
You must make sure you implement the ASGI protocol correctly and send
the correct ASGI events if something goes wrong.

[asgi]: https://asgi.readthedocs.io
