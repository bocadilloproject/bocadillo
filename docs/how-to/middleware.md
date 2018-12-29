# Writing middleware

::: warning
This feature is **experimental**; the middleware API may be subject to changes.
:::

[Middleware] act as wrapper around your Bocadillo application in order to extend its behavior globally. They come in 2 flavors: regular middleware and ASGI middleware.

## Regular middleware

Regular middleware (or just *middleware*) is the standard, higher-level API for middleware in Bocadillo. They provide two hooks, namely `before_dispatch()` and `after_dispatch()`, that are called respectively before and after a request is dispatched and a response is obtained.

To write a middleware, create a subclass of `bocadillo.Middleware` and implement `.before_dispatch()` and `.after_dispatch()` as seems fit.

The following is a (contrived) example that prints the URL of the request and the response to the console:

```python
import bocadillo

class PrintUrlMiddleware(bocadillo.Middleware):

    async def before_dispatch(self, req):
        print(req.url)
    
    async def after_dispatch(self, req, res):
        print(res.url)
```

::: tip
The `.before_dispatch()` and `.after_dispatch()` can also be plain, non-`async` Python functions.
:::

You may also override `__init__()` to perform extra initialisation logic. Be sure to keep the following signature: `(self, dispatch, **kwargs) -> None` and to call `super()`.

```python
import bocadillo

class PrintUrlMiddleware(bocadillo.Middleware):
    
    def __init__(self, dispatch, flag=False, **kwargs):
        super().__init__(dispatch, **kwargs)
        # Do stuff based on `flag`
```

Users will be able to register the middleware using `api.add_middleware()`:

```python
api = bocadillo.API()
api.add_middleware(PrintUrlMiddleware, flag=True)
```

## ASGI middleware

In order to support lower-level middleware needs, you can also write a middleware class that implements the [ASGI] interface directly. For example:

```python
class PrintUrlMiddleware:

    def __init__(self, api):
        self.api = api

    def __call__(self, scope: dict):
        if scope['type'] == 'http':
            # TODO: do something based on scope
            pass
        return self.api(scope)
```

::: warning
Because ASGI middleware wrap the API object itself, no error handling can be performed by Bocadillo. You must strictly implement the ASGI protocol and return an HTTP response yourself in case something goes wrong.
:::

Most likely, you won't need to write ASGI middleware yourself. The possibility is only documented to justify the existence of `api.add_asgi_middleware()`, which is generally used for third-party middleware provided as an ASGI application.

[Middleware]: ../topics/http/middleware.md
