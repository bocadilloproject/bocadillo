# HTTP middleware

::: warning
This feature is **experimental**; the middleware API may be subject to changes.
:::

The HTTP middleware framework is a lightweight system to plug into the processing of HTTP requests and responses. It is an HTTP-specific solution that is arguably higher-level than [ASGI middleware].

## How middleware is applied

When a middleware class is registered, it **wraps** the already registered middleware.

Because of this, it is convenient to think of middleware as being organized in **layers**, and we'll refer to **outer middleware** and **inner middleware**.

What this means is that middleware classes effectively chain the responsibility of dispatching the request down to the router of the application, resulting in a chain of callbacks illustrated below:

```python
await M1.before_dispatch(req, res)
    await M2.before_dispatch(req, res)
        ...
            await Mn.before_dispatch(req, res)
                await http_router(req, res)
            await Mn.after_dispatch(req, res)
        ...
    await M2.after_dispatch(req, res)
await M1.after_dispatch(req, res)
```

So, when processing an incoming HTTP request, HTTP middleware is applied in a stack-like manner.

More specifically, each middleware:

1. Is given the `Request` and `Response` from its _outer_ middleware.
2. Processes them if needed (`.before_dispatch()` hook).
3. Gets a `Response` from its _inner_ middleware (a.k.a delegation).
4. Processes it if needed (`.after_dispatch()` hook).
5. Returns it to its _outer_ middleware.

## Default middleware

Two HTTP middleware are registered on every application:

- [`HTTPErrorMiddleware`](../../api/errors.md#httperrormiddleware) is responsible for calling a suitable [error handler](./error-handling.md) when an exception, if it can.
- [`ServerErrorMiddleware`](../../api/errors.md#servererrormiddleware) is responsible for catching unhandled exceptions and returning 500 errors when one occurs.

## Using middleware

When given a midleware class, you can register it on an application using `app.add_middleware()`:

```python
app.add_middleware(SomeHTTPMiddleware, foo='bar')
```

All keyword arguments passed to `app.add_middleware()` will be passed to the middleware constructor upon startup.

## Writing middleware

If you're interested in writing your own HTTP middleware, see our [Writing middleware] how-to guide.

[writing middleware]: ../../how-to/middleware.md
[asgi]: https://asgi.readthedocs.io
[asgi middleware]: ../agnostic/asgi-middleware.md
