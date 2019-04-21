---
title: "Bocadillo 0.14 released!"
description: "All-async, app configuration, JSON data validation, route and query parameter validation, Bocadillo CLI, plugin framework, and more!"
date: 2019-04-24
author: Florimond Manca
layout: Post
---

We're very excited to anounce that Bocadillo v0.14 is out! This release standardises how applications are structured and run, and brings new features that make working with Bocadillo even more productive.

If you have any questions or feedback about this release, feel free to [get in touch](/faq/#getting-in-touch)!

::: warning IMPORTANT
**Bocadillo 0.14.0 is incompatible with 0.13.x and earlier**. We took the decision to introduce breaking changes to improve the API and the overall development workflow. You'll find tips on migrating from 0.13.x in this blog post.
:::

#### Contents

[[toc]]

## Non backwards-compatible changes

### All async

::: tip tl;dr
From 0.14 and onwards, when in doubt, use `async def`.
:::

Since the very first releases, Bocadillo was designed to support both synchronous and asynchronous syntax in a lot of places. This design principle was known as **async-first**.

However, this introduced complexity in the framework internals, and it was not clear where async was mandatory and where it was not. We realised that async-first was not the right approach.

For this reason, **Bocadillo v0.14 and onwards will be _all-async_**.

This means that **synchronous syntax for the following features is not supported anymore**: function-based HTTP views, methods of class-based HTTP views, error handlers, HTTP middleware callbacks, and HTTP hooks.

For example, you can't write this in Bocadillo v0.14+ anymore:

```python
@app.route("/")
def index(req, res):
    pass
```

Instead, you _must_ use `async def`:

```python
@app.route("/")
async def index(req, res):
    pass
```

To help with the transition:

1. We've added checks to the framework that detect when you use a regular function whereas an asynchronous one is expected.
2. We've added an [async crash course](/guides/async.md) with tips, common patterns, and resources for people getting started with Python async.

We hope this decision will foster your interest in learning about async Python, and make working with Bocadillo more straight-forward!

### Application configuration

Before 0.14, configuration was primarily performed via arguments to `App`, e.g. `App(enable_hsts=True)`.

This proved to be hardly scalable, because:

- More and more parameters were added to `App` as we implemented new features.
- Decomposing an app into multiple sub-apps required to configure them in the same way — when this didn't cause strange errors because of duplicated configuration.

To help with this, **Bocadillo 0.14 completely changes the way applications are configured** using a new configuration workflow supported by a lightweight plugin system.

::: tip
This new way of doing things induces some necessary boilerplate, so to help you out we recommend you use the new [Bocadillo CLI](#bocadillo-cli).
:::

#### Configuration workflow

App configuration is now performed once and for all with the `bocadillo.configure()` helper. It accepts various **settings** which are then made accessible anywhere using the `bocadillo.settings` object.

As for where and how those settings should be defined, the TL;DR is: use a **settings module**.

To learn more, please refer to the new [Configuration](/guides/architecture/app.md#configuration) guide.

#### Plugins

Plugins are small pieces of functionality which are setup at configuration time.

Many features in Bocadillo are now implemented as plugins. As a result, **`App` does not take any parameter anymore**. Instead, you should define plugin-specific **settings** in the settings module. These are specified in the [plugins API reference](/api/plugins.md).

What does this mean in practice? Well, instead of:

```python
# project/app.py
from bocadillo import App

app = App(enable_hsts=True)
```

Use:

```python
# project/settings.py
HSTS = True

# project/app.py
from bocadillo import App, configure
from . import settings

app = App()
configure(app, settings)
```

If this looks like writing more code, it's because it is — except you're now _doing things right_.

To help with this necessary boilerplate, be sure to check out [Bocadillo CLI](#bocadillo-cli) and its project creation command.

### Serving apps

Previously, the idiomatic way to serve apps was to add

```python
if __name__ == "__main__":
    app.run()
```

at the end of the `app.py` script and to run `$ python app.py`.

We concluded that this early design decision was bad, because:

- It increases boilerplate.
- The `if __name__ == "__main__"` check can be confusing for beginners (and even more seasoned Python developers).
- `app.run()` was merely a proxy for `uvicorn.run()` with little to no added value.

For this reason, **`app.run()` has been removed entirely**. This has two consequences:

1. The official way to serve apps is now to **use the `uvicorn` command**. See [Serving an application](/guides/architecture/app.md#serving-an-application).
2. **Debug mode has been removed.** You can enable hot reload using the `--reload` option to `uvicorn`.

Here's a comparison of the minimum working application with hot reload enabled:

- Previously:

```python
# app.py
from bocadillo import App

app = App()

if __name__ == "__main__":
    app.run(debug=True)
```

```bash
python app.py
```

- Now:

```python
from bocadillo import App, configure

app = App()
configure(app)
```

```bash
uvicorn app:app
```

### res.json

Previously, sending a JSON response was performed using `res.media`. We reckon that this was not very intuitive. Since [media has been removed](#media), **we decided to replace `res.media` by the more straight-forward `res.json`**:

```python
@app.route("/health-check")
async def health_check(req, res):
    # ❌ Previously:
    res.media = {"status": "OK"}
    # ✅ Now:
    res.json = {"status": "OK"}
```

### `Redirect` exception

Previously, redirecting an HTTP request to another URL was performed using the `app.redirect()` helper method. The fact that this method interrupted the execution of a view without a `return` or a `raise` felt like unnecessary magic. With the removal of [named routes](#named-routes), we decided to fix this.

Redirections are now performed by raising a `Redirect` exception (which is exactly what `app.redirect()` did internally). Redirecting to another route by name is not supported anymore: you need to pass the full URL.

```python
from bocadillo import App, Redirect

app = App()

@app.route("/hello/{name}")
async def hello(req, res, name: str):
    res.text = f"Hello, {name}!"

@app.route("/")
async def index(req, res):
    # ❌ Previously, one of:
    app.redirect("hello", name="Stranger")
    app.redirect(url="/hello/Stranger")
    # ✅ Now:
    raise Redirect("/hello/Stranger")
```

## New features

### Bocadillo CLI

[Bocadillo CLI] is a brand new CLI to help with bootstrapping Bocadillo projects. It aims at **standardizing** how Bocadillo projects are structured, and simplify the overall workflow, especially for beginners.

[bocadillo cli]: https://github.com/bocadilloproject/bocadillo-cli

In particular, `bocadillo create <PROJECT_NAME>` instantly generates a project with all the files you need to just start writing code, instead of figuring out how files should be structured! 🚀

Digging it? [Give Bocadillo CLI a star!][bocadillo cli]

![](https://user-images.githubusercontent.com/15911462/56270267-098d7e80-60f6-11e9-9b76-8434b684e179.png)

### Data validation

This one is pretty exciting. There's been a gap in the framework as to how JSON data should be validated, and with what tools.

In 0.14, you can now **use the [TypeSystem](https://www.encode.io/typesystem) library to validate and serialize JSON data**. 🎉

To learn more, read [JSON validation](/guides/http/json-validation.md).

### Route parameter validation

Route parameters can now be validated using type annotations.

As a result, you can't use format specifiers anymore. So instead of `{pk:d}` in the URL pattern, use:

```python
@app.route("/users/{pk}")
async def get_user(req, res, pk: int):
    pass
```

For advanced validation use cases, you can annotate the route parameter with a TypeSystem field.

Learn more in [Route parameter validation and conversion](/guides/http/routing.md#validation-and-conversion).

### Query parameter injection

Besides being available on `req.query_params`, query parameters can now be injected into the view by declaring them as a parameter with a default.

Bonus points: query parameters injected like this are validated just like route parameters!

As a result, the following code:

```python
@app.route("/users")
async def get_users(req, res):
    token = req.query_params.get("token")
```

Can be refactored to:

```python
@app.route("/users")
async def get_users(req, res, token: str = None):
    pass
```

Learn more in [Query parameters](/guides/http/routing.md#query-parameters).

### Exceptions in error handlers

Exceptions raised within an error handler are now fed back into the error handling pipeline. This allows to build modular and reusable error handlers.

For example, you can now re-raise an `HTTPError` in a custom error handler:

```python
from bocadillo import App, HTTPError

app = App()

class Nope(Exception):
    pass

@app.error_handler(Nope)
async def on_nope(req, res, exc):
    raise HTTPError(403, detail="We can't let you do this!")
```

## Removed features

### Media

The media framework allowed to configure the _media type_ of an application globally and to abstract the exact serialization via media handlers. This feature brought inner complexity and quirks, and was very rarely used for anything else than JSON, the de-facto standard for Web APIs nowadays.

As a result, `res.media`, the `media_type` parameter to `App` as well as `@app.media_handler` and `app.add_media_handler()` were removed.

To send JSON data in the response, use [res.json](#res-json) instead.

### Named routes

Previously, all HTTP routes were given a name which could be used to reverse URLs via the `app.url_for()` helper.

Due to the complexity introduced compared to how useful this shortcut turns out to be, **named routes and URL reversion have been removed**. This means that:

- `@app.route()` does not have the `name` and `namespace` parameters anymore.
- `app.url_for()` and the `url_for` templates variable don't exist anymore.

If you want the full URL to a view, you'll simply need to build it yourself.

### Test client with `app.client`

Accessing the test client via `app.client` was deprecated in 0.13. It is now definitively removed. You must use `bocadillo.create_client()` instead, as described in [Testing](/guides/architecture/testing.md).
