# Writing middleware

Middleware classes act as wrappers around your Bocadillo application in order to extend its behavior globally.

They come in 2 flavors: [HTTP middleware](../guides/http/middleware.md) and [ASGI middleware](../guides/agnostic/asgi-middleware.md).

## HTTP middleware

### Basic usage

The HTTP middleware framework provides two hooks, namely `before_dispatch()` and `after_dispatch()`, which are called respectively before and after an HTTP request is dispatched and an HTTP response is obtained.

Each hook is given the current `Request` and `Response` objects
(the same that will be passed down to the views) and can alter them as is
required to achieve the desired behavior.

A bare-bones middleware looks like this:

```python
from bocadillo import Middleware, Request, Response

class TransparentMiddleware(Middleware):

    async def before_dispatch(self, req: Request, res: Response):
        pass
       
    async def after_dispatch(self, req: Request, res: Response):
        pass
```

::: tip
The `.before_dispatch()` and `.after_dispatch()` can also be plain, non-`async` Python functions.
:::

### Interrupting request processing

If the `before_dispatch` hook returns the `Response` object, no further
processing is performed.

For example, this middleware will result in a `202 Accepted: Foo` response being
returned for *any* request made to the application.

```python{8}
from bocadillo import Middleware, Request, Response

class FooMiddleware(Middleware):

    async def before_dispatch(self, req: Request, res: Response):
        res.text = "Foo"
        res.status_code = 202
        return res
```

Note: returning a response in `after_dispatch` has no effect.

### Configuration

Keyword arguments passed to `app.add_middleware()` as passed down to the
middleware's `__init__()` method. This means that you can grab them there to
perform extra initialisation logic.

```python
from bocadillo import Middleware

class MaybeMiddleware(Middleware):
    
    def __init__(self, *args, flag=False, **kwargs):
        super().__init__(*args, **kwargs)
        if flag:
            # Do stuff if flag is True
            pass
```

Users will be able to register the middleware using `app.add_middleware()`:

```python
app = App()
app.add_middleware(MaybeMiddleware, flag=True)
```

### Middleware from scratch

As it turns out, the `before_dispatch()` and `after_dispatch()` hooks on
`Middleware` are just helpers.

If they don't fit your needs, you can also implement the `__call__()` method directly.

Subclassing from `Middleware` will ensure that you are still given the
underlying HTTP `app` and keyword arguments passed upon registering the
middleware. 

```python
from bocadillo import Request, Response, Middleware

class TransparentMiddleware(Middleware):

    def __call__(self, req: Request, res: Response) -> Response:
        return await self.app(req, res)
```

## ASGI middleware

In order to support lower-level middleware needs, you can also write a
middleware class that implements the [ASGI] interface directly.

```python
class SpecialPathMiddleware:

    def __init__(self, app, special_path: str = "special"):
        self.app = app
        self.path = special_path
    
    def special(self, scope: dict):
        async def asgi(receive, send):
            # TODO: do something special
            pass
        return asgi

    def __call__(self, scope: dict):
        if scope["path"] == self.path:
            return self.special(scope)
        return self.app(scope)
```

::: warning
Bocadillo is not able to perform error handling at the ASGI middleware level.
You must make sure you implement the ASGI protocol correctly and send
the correct ASGI events if something goes wrong.
:::

While ASGI middleware is very low-level, it also means that
third-party middleware classes implemented in this form can be plugged in without
extra plumbing. 

[ASGI]: https://asgi.readthedocs.io
