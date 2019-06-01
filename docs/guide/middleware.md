# Middleware

<Badge type="warn" text="Experimental"/>

Bocadillo middleware is a lightweight system to plug into the processing of requests and responses.

It comes in two flavors:

- HTTP middleware: higher-level, but specific to HTTP endpoints.
- ASGI middleware: lower-level, but applied to both HTTP and Websocket endpoints.

## The middleware stack

When a middleware class is registered, it **wraps** the already registered middleware.

Because of this, it is convenient to think of middleware as being organized in **layers**. Each middleware has an **outer middleware** and an **inner middleware**.

What this means is that middleware classes effectively chain the responsibility of dispatching the request down to the router of the application.

## Using middleware

When given a middleware class, and regardless of its type (HTTP or ASGI), you can register it on an application using `app.add_middleware()`.

```python
app.add_middleware(SomeMiddleware, foo="bar")
```

All keyword arguments passed to `.add_middleware()` get passed to the middleware constructor.

## Default middleware

The default middleware classes registered on every application are documented in the [middleware API reference](/api/middleware.md).

## Writing HTTP middleware

HTTP middleware should inherit from [`Middleware`](/api/middleware.md#middleware), a base class which provides two hooks:

- `.before_dispatch()`: called before the request is dispatched (i.e. processed by the inner middleware).
- `.after_dispatch()`: called after the request has been dispatched.

Each hook is given the current `Request` and `Response` objects, and can alter them as necessary to achieve the desired behavior.

A "do nothing" HTTP middleware looks like this:

```python
from bocadillo import Middleware

class NoOpMiddleware(Middleware):
    async def before_dispatch(self, req, res):
        pass

    async def after_dispatch(self, req, res):
        pass
```

If the `.before_dispatch()` hook returns the `Response` object, no further
processing is performed.

For example, this middleware will result in a `202 Accepted` response being
returned for any request made to the application:

```python
from bocadillo import Middleware

class Always202Middleware(Middleware):
    async def before_dispatch(self, req, res):
        res.status_code = 202
        return res
```

If you need the middleware to have some kind of state or configuration, you can override `.__init__()` and accept extra parameters:

```python
from bocadillo import Middleware

class MessageMiddleware(Middleware):
    def __init__(self, inner, message: str):
        super().__init__(inner)  # Don't forget to call `super()`!
        self.message = message

    async def before_dispatch(self, req, res):
        print("MESSAGE:", self.message)
```

Example usage:

```python
app.add_middleware(MessageMiddleware, message="Hello, middleware!")
```

## Writing ASGI middleware

If you need global behavior that does not only apply to HTTP, you can go bare-metal and use ASGI middleware classes. They are lower-level middleware classes that implement the [ASGI](https://asgi.readthedocs.io) protocol directly.

Just like HTTP middleware, an ASGI middleware's `.__init__()` method can extra parameters for configuration purposes.

::: tip CHANGED IN 0.15
There is no `ASGIMiddleware` base class anymore.
:::

For example, here is the ASGI equivalent of the HTTP `MessageMiddleware` from the previous section:

```python
from bocadillo import App

class ASGIMessageMiddleware:
    def __init__(self, app, message: str):
        self.app = app
        self.message = message

    async def __call__(self, scope, receive, send):
        print("MESSAGE:", self.message)
        await self.app(scope, receive, send)
```

::: warning
Here, `app` represents the **inner ASGI application** (which is very likely to be another middleware). It does not represent a Bocadillo `App` instance.
:::

Example usage:

```python
app.add_middleware(ASGIMessageMiddleware, message="Hello, middleware!")
```

## Error handling

Exceptions raised in middleware (be it HTTP or ASGI middleware) are handled exactly as described in [Error handling (Essentials)](https://bocadilloproject.github.io/guide/errors.html).

In particular, this means you can raise exceptions such as `HTTPError` in the `.before_dispatch()` or `.after_dispatch()` methods or an HTTP middleware, or in the `.__call__()` method or an ASGI middleware.
