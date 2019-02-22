# HTTP middleware

::: warning
This feature is **experimental**; the middleware API may be subject to changes.
:::

The HTTP middleware framework is a lightweight system to plug into the processing of HTTP requests and responses. It is an HTTP-specific solution that is arguably higher-level than [ASGI middleware].

## How middleware is applied

HTTP middleware is applied in a stack-like manner. A middleware is given the request from the middleware above it, processes it (`before_dispatch()` hook), gets a response from the middleware beneath it, processes it too (`after_dispatch()` hook) and returns it (i.e. to the middleware above).

Because of this, middleware classes effectively chain the responsibility of dispatching the request down to the router of the application object, resulting in a chain of callbacks illustrated below.

```
M1.before_dispatch(req)
    M2.before_dispatch(req)
        ...
            Mn.before_dispatch(req)
                res = app.dispatch(req)
            Mn.after_dispatch(req, res)
        ...
    M2.after_dispatch(res)
M1.after_dispatch(res)
```

## Using middleware

HTTP middleware takes the form of middleware classes that subclass the `bocadillo.Middleware` class.

You can register an HTTP middleware class with `app.add_middleware()`:

```python
app.add_middleware(SomeHTTPMiddleware, foo='bar')
```

All keyword arguments passed to `add_middleware()` will be passed to the middleware constructor upon startup.

::: tip NOTE
Registering a middleware effectively **wraps** it around the application and the already registered middleware.

In practice, this means that the following registration:

```python
app.add_middleware(M1)
app.add_middleware(M2)
```

will result in the following processing chain:

```
M2.before_dispatch(req)
    M1.before_dispatch(req)
        res = app.dispatch(req)
    M1.after_dispatch(res)
M2.after_dispatch(res)
```

Most of the times, though, this should not matter — middleware should be designed to be as independent form one another as possible.
:::

If you're interested in writing your own HTTP middleware, see our [Writing middleware] how-to guide.

[writing middleware]: ../../how-to/middleware.md
[asgi]: https://asgi.readthedocs.io
[asgi middleware]: ../agnostic/asgi-middleware.md
