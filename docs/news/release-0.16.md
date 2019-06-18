---
title: "What's new in Bocadillo 0.16"
description: "Bocadillo 0.16 has been released! Learn what's in it for you: routers, plugin registration, unified middleware, and more."
date: 2019-06-01
author: Florimond Manca
layout: Post
---

If you have any questions or feedback about this release, feel free to [get in touch](https://bocadilloproject.github.io/faq.html#getting-in-touch)!

[[toc]]

## Routers

**Routers** are a new and powerful way of **splitting applications** into more manageable chunks.

For example, you can create an authentication router…

```python
# myproject/routers/auth.py
from bocadillo import Router

router = Router()

@router.route("/login", methods=["post"])
async def login(req, res):
    ...

@router.route("/logout", methods=["post"])
async def logout(req, res):
    ...
```

…and include it into the main app later on:

```python
# myproject/app.py
from bocadillo import App
from .routers import auth

app = App()
app.include_router(auth.router)
```

To learn more, read the new [Routers](https://bocadilloproject.github.io/guide/routers.html) guide.

## Plugin registration

The plugin system built into Bocadillo allows to build settings-based features. In fact, many built-in Bocadillo features are implemented using plugins. Yet, there was no easy way to register custom plugins… Until now!

You can use the new `PLUGINS` setting to register your own or third-party Bocadillo plugins into your application.

As a concrete example, let's write a plugin which registers the `auth` router we wrote earlier:

```python
# myproject/plugins.py
from .routers import auth

def use_auth(app):
    app.include_router(auth.router)
```

(Note that plugins do not need the `@plugin` decorator anymore. This decorator is now deprecated and will be removed in the next minor release.)

We can now add the `use_auth` plugin to the list of `PLUGINS`:

```python
# myproject/settings.py
from .plugins import use_auth

PLUGINS = [use_auth]
```

This may seem like an extra level of indirection, but it's actually a cleaner way to add functionality to an application.

For example, we can use **conditional registration** to apply the plugin only if the `ENABLE_AUTH` environment variable is set:

```python
# myproject/settings.py
from starlette.config import Config
from .plugins import use_auth

config = Config(".env")

PLUGINS = [
    {use_auth: config("ENABLE_AUTH", cast=bool, default=True)}
]
```

You can now control whether auth routes are exposed via environment variables!

We hope this settings-based plugin registration API will enable Bocadillo users to share and reuse plugins more easily.

To learn more about this, read the updated [Plugins](https://bocadilloproject.github.io/guide/plugins.html) guide.

## Unified middleware

When registering middleware, there was previously a distinction between HTTP middleware (using `app.add_middleware()`) and ASGI middleware (using `app.add_asgi_middleware()`).

Thanks to an internal refactoring, all middleware can now be registered via `app.add_middleware()`. As a result, `app.add_asgi_middleware()` is now deprecated.

Besides, exceptions raised in ASGI middleware are now processed by error handlers. For example, you can `raise HTTPError(400)` and Bocadillo will return a `400 Bad Request` response like it would in views or HTTP middleware.

We think all this will help make working with middleware more enjoyable and straight-forward.

To learn more, read the updated [Middleware](https://bocadilloproject.github.io/guide/middleware.html) guide.

## Miscellaneous

### Trailing slash redirects

If the requested URL path does not end with a trailing slash, e.g. `/items`, Bocadillo now appends one and redirects clients to the new URL, e.g. `/items/`.

This prevents clients from obtaining a confusing `404 Not Found` error simply because they forgot to add a trailing slash.

If necessary, you can opt out using the `REDIRECT_TRAILING_SLASH` setting.

To learn more, read [About trailing slashes](https://bocadilloproject.github.io/guide/routing.html#about-trailing-slashes).

### HTTP methods

From 0.16, HTTP methods on function-based views can be specified more simply using the `methods=` argument to `@route()`:

```python
@app.route("/items", methods=["post"])
async def create_item(req, res):
    ...
```

Previously, you had to use the (now deprecated) `@view()` decorator:

```python
from bocadillo import view

@app.route("/items")
@view(methods=["post"])
async def create_item(req, res):
    ...
```

See also: [HTTP methods](https://bocadilloproject.github.io/guide/routing.html#http-methods).

### Constants

The `ALL_HTTP_METHODS` constant (from `bocadillo.constants`) now contains HTTP methods in lowercase, instead of uppercase.

### `res.media`

`res.media` has deprecated since 0.14, and it has now been removed. Please use `res.json` instead. For more information, see [Sending content](https://bocadilloproject.github.io/guide/responses.html#sending-content).
