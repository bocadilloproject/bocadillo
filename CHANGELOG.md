# Changelog

All notable changes to Bocadillo are documented here.

The format of this document is based on [Keep a Changelog](https://keepachangelog.com).

**Versioning policy**

Bocadillo adheres to [Semantic Versioning](https://semver.org), BUT…

Bocadillo is still in **Alpha** (< 1.0) version. As such, breaking API changes will only cause **minor** version bumps instead of major ones until v1.0 is reached.

As a result, we strongly recommend you read this document carefully before upgrading to any new alpha version. Breaking API changes will be denoted with a **BREAKING** prefix.

## [Unreleased]

### Added

- Route parameters are now validated based on type annotations defined on the HTTP or WebSocket view. Annotations can be `int`, `float`, `bool`, `date`, `datetime`, `time`, `decimal.Decimal` or any [TypeSystem] field.
- Query parameters can be injected into a view by declaring them as parameters with defaults, e.g. `limit: int = None`. Type annotation-based validation is also available.
- Error handlers can now re-raise exceptions for further processing, e.g. re-raise an `HTTPError` which will be processed by the registered `HTTPError` handler.

[typesystem]: https://www.encode.io/typesystem

### Fixed

- The code base now uses `__slots__` in all relevant places. We expect some speed improvements as a result.

### Removed

- **BREAKING**: route parameter validation via specifiers (e.g. `{id:d}`) is not supported anymore. Please use type annotation-based validation instead (e.g. `pk: int`).

Deprecated items from 0.13:

- **BREAKING**: `.client` attribute on `App` and `Recipe` was removed. Please use `bocadillo.testing.create_client` instead.

## [v0.13.1] - 2019-03-19

### Changed

- WebSocket auto-accept: in order to reduce boilerplate for common use cases, WebSocket endpoints now automatically `.accept()` and `.close()` the connection (or, equivalently, enter with `async with ws:` block). This is backwards compatible: entering `async with ws:` has no effect if the connection has already been accepted. Revert to the old behavior by passing `auto_accept=False` to `@app.websocket_route()`.

## [v0.13.0] - 2019-03-16

Supporting blog post: [Bocadillo 0.13 released!](https://bocadilloproject.github.io/blog/release-0.13.md)

### Added

Features:

- Providers: explicit, modular and flexible runtime dependency injection system, inspired by pytest fixtures. Implemented via [aiodine].
- Server-Sent Event support:
  - Define an event stream with `@res.event_stream`.
  - Format SSE messages with `server_event`.
- Cookie-based sessions: set the `SECRET_KEY` environment variable, and access/modify via `req.session`.
- New base class for ASGI middleware: `ASGIMiddleware`. In the docs, old-style ASGI middleware has been rebranded as "pure" ASGI middleware.
- Testing helpers: `create_client`, `LiveServer`.
- Add an `override_env` utility context manager.

[aiodine]: https://github.com/bocadilloproject/aiodine

Documentation:

- Testing guide.
- How-to guide on integrating with pytest.
- Chatbot server tutorial.

### Changed

- HTTP middleware classes can now expect both the `inner` middleware _and_ the `app` instance to be passed as positional arguments, instead of only `inner`. This allows to perform initialisation on the `app` in the middleware's `__init__()` method. The same goes for the new `ASGIMiddleware` base class.

### Fixed

- Stream responses (and SSE streams by extension) now stop as soon as a client disconnects. For custom disconnect handling, use `raise_on_disconnect=True` and handle `bocadillo.request.ClientDisconnect` yourself.
- ASGI middleware is now applied even when the request is routed to a sub-application (e.g. a recipe). In the past, this could lead to CORS headers not being added on a recipe despite them being configured on the root application.

### Deprecated

- `app.client` has been deprecated in favor of the `create_client` testing helper, and will be removed in v0.14. For pytest users, consider building and using a `client` fixture in your tests:

```python
# tests.py
import pytest
from bocadillo.testing import create_client

from myproject import app

@pytest.fixture
def client():
    return create_client(app)

def test_stuff(client):
    ...
```

### Removed

Deprecated items from 0.12:

- **BREAKING**: the `API` class was removed. Use `App` now.
- **Breaking**: the `template*` methods on `App` no longer exists. Use the `Templates` helper instead.

## [v0.12.6] - 2019-03-09

### Fixed

- Missing `headers` and `query_params` attributes on `WebSocket`.

## [v0.12.5] - 2019-03-06

### Fixed

- A bug from v0.12.4 disallowed the creation of an application in a Python interpreter. This has been fixed.

## [v0.12.4] - 2019-03-05

### Added

- Add support for uvicorn 0.5.x.
- Activate debug mode via the `BOCADILLO_DEBUG` environment variable.

### Fixed

- When launching the application script in debug mode, hot reload was activated but it did not actually reload the application in case of changes. This has been fixed. Caveat: the application should be declared as `app` in the application script, but this can be overridden via the `declared_as` parameter to `App.run`.

## [v0.12.3] - 2019-03-04

### Fixed

- Hot fix: pin Uvicorn to <0.5 while we investigate compatibility with 0.5+.

## [v0.12.2] - 2019-03-01

### Added

- Pass extra WhiteNoise configuration attributes using `App(static_config=...)`.

### Fixed

- Changes to static files are now picked up in debug mode.

## [v0.12.1] - 2019-02-28

### Fixed

- Installing from `pip` now checks that Python 3.6+ is installed.

## [v0.12.0] - 2019-02-22

This release contains replacements for important features (`API`, app-level template rendering). Their old usage has been deprecated but is still available until the next minor release.

This means that _there shouldn't be any breaking changes_. If you do experiment breaking changes, please report them to us!

### Added

- API reference for the `Response` and `Request` classes.
- Browser-downloadable responses (a.k.a attachments) with `res.attachment`. This is a handy shortcut for setting the `Content-Disposition` header.
- (Asynchronous) file responses with `res.file()`.
- Generic templating with `bocadillo.templates.Templates`.

### Changed

- The main application class is now called `App`. `API` is still available as an alias.
- Content types are now available on the `bocadillo.constants.CONTENT_TYPE` enum, instead of `bocadillo.media.Media`.
- Recipes are now just apps: they expose all the parameters, attributes and methods that an `App` exposes.

### Fixed

- `Response.text` and `Response.html` are now proper write-only Python properties, which should be more friendly with type checkers.

### Deprecated

- `API` has been deprecated in favor of `App`. It will be removed in v0.13.0.
- The `.template`, `.template_sync` and `.template_string` methods on `App` and `Recipe` have been deprecated in favor of generic templating. They will be removed in v0.13.0.

### Removed

- The `handle_text` media handler has been removed due to how `Response.text` and `Response.html` now work.

## [v0.11.2] - 2019-02-21

### Fixed

- Using `await req.form()` previously required to install a third-party library, `python-multipart`, which is now bundled by default.

## [v0.11.1] - 2019-02-19

### Fixed

- Fixed a bug that caused import errors when using Starlette < 0.11.

## [v0.11.0] - 2019-02-11

### Fixed

- A parser for URL patterns used to be compiled on every call to a route. The parser is now compiled once and for all on startup. As a result, URL matching is slightly faster.

### Changed

- New colors and logo for the docs site.
- Various documentation improvements.

### Removed

- **BREAKING**: Boca was moved to a separate package: [boca](https://bocadilloproject.github.io/boca/). It can be installed from PyPI using `pip install boca` and does not come installed with Bocadillo by default.

## [v0.10.3] - 2019-02-02

### Fixed

- Better documentation about route parameters, including how to implement wildcard matching.
- Previously, it was not possible to create a catch-all route using the pattern `{}` because a leading slash was automatically added, preventing the pattern from matching a request to the root URL `/`. This has been fixed!

## [v0.10.2] - 2019-01-27

### Added

- Recipes now support redirections, e.g. `recipe.redirect(name="recipe:foo")`.

### Fixed

- Using `url_for()` in a template rendered from a recipe (e.g. `await recipe.template()`) used to raise an `UndefinedError`. This has been fixed.

## [v0.10.1] - 2019-01-21

### Changed

- Now requires `uvicorn>=0.3.26`.

### Fixed

- Fixed a bug that caused an `ImportError` when importing from
  `bocadillo.api` using `uvicorn<0.3.26`.

## [v0.10.0] - 2019-01-17

### Added

- In-browser traceback of unhandled exceptions when running with `debug=True`.
- Various documentation improvements and additions, e.g. databases discussion and Tortoise ORM how-to.

### Changed

- The `before_dispatch` hook on HTTP middleware classes now takes a `Response` as second argument.
- The `bocadillo.exceptions` module has been removed:
  - `WebSocketDisconnect` has moved to `bocadillo.websockets`.
  - `UnsupportedMediaType` has moved to `bocadillo.media`.
  - `HTTPError` has moved to `bocadillo.errors` (but is still available at the top level: `from bocadillo import HTTPError`).
- Other internal refactoring that should not affect framework users.
- Discussions are now in a separate section in the documentation.

### Fixed

- Even if an error handler was registered for a given exception class, Bocadillo used to return a 500 error response. It will now honor what the error handler does to the `res` object, i.e. only returning a 500 error response if the error handler does so or if it re-raised the exception.
- The `after_dispatch` hook on HTTP middleware classes is not called anymore if the inbound HTTP method is not supported by the view.

### Removed

- `RoutingMiddleware` was removed as it had been deprecated since v0.8.

## [v0.9.1] - 2018-01-04

### Fixed

- Add missing `url` attribute on `WebSocket` objects, which prevented accessing information about the URL from WebSocket views.

## [v0.9.0] - 2018-01-03

This release has **breaking API changes** due to an overhaul of the view system.

If your application uses the features below, you are most likely affected and should review these changes thoroughly before upgrading:

- Use hooks via `@api.before()` or `@api.after()`.
- Restriction of HTTP methods via the `methods` parameter to `@api.route()`.

### Added

- Support for WebSockets, including routing with `@api.websocket_route()`.
- Send a chunk-encoded response with `res.chunked = True`.
- Support for request and response streaming with `async for chunk in req` and `@res.stream`.
- View definition utilities: `from_handler()`, `from_obj()`, `@view()`.
- In particular, the `@view()` decorator (available as `from bocadillo import view`) accepts a `methods` argument originally used by `@api.route()` . Plus, passing the `all` built-in has the same effect as defining `.handle()` on the analogous class-based view — i.e. supporting all HTTP methods.
- Function-based views are automatically decorated with `@view()` to ensure backwards compatibility.

```python
from bocadillo import API, view

api = API()

# This:
@api.route("/")
async def index(req, res):
    pass

# Is equivalent to:
@api.route("/")
@view()
async def index(req, res):
    pass

# Which is equivalent to:
@api.route("/")
@view(methods=["get"])
async def index(req, res):
    pass

# Which is itself *strictly* equivalent to:
@api.route("/")
class Index:
    async def get(self, req, res):
        pass
```

- API reference for the `views` module.
- Various documentation additions and improvements.

### Changed

- **BREAKING**: hooks were moved to a separate module: `bocadillo.hooks`. You must now use `@hooks.before()` / `@hooks.after()` instead of `@api.before()` / `@api.after()` and `@recipe.before()` / `@recipe.after()`.
- **BREAKING**: hooks must now be placed right above the view being decorated. This affects both function-based views and class-based views (but not method views).

```python
from bocadillo import API, hooks

api = API()

async def before(req, res, params):
    print("before!")

# < 0.9
@api.before(before)
@api.route("/")
async def foo(req, res):
    pass

@api.before(before)
@api.route("/")
class Foo:
    pass

# >= 0.9:
@api.route("/")
@hooks.before(before)
async def foo(req, res):
    pass

@api.route("/")
@hooks.before(before)
class Foo:
    pass
```

### Removed

- **BREAKING**: the `methods` argument to `@api.route()` has been removed. To specify allowed methods on function-based views, you must now use the `@view()` decorator — see below.

```python
from bocadillo import API, view

api = API()

# < 0.9
@api.route("/", methods=["post"])
async def foo(req, res):
    pass

# >= 0.9
@api.route("/")
@view(methods=["post"])
async def foo(req, res):
    pass
```

- Removed dependency on `async_generator`.

## [v0.8.1] - 2018-12-27

### Changed

- `await req.json()` now returns a `400 Bad Request` error response if the input JSON is malformed, which allows to skip handling the `JSONDecodeError` manually.

## [v0.8.0] - 2018-12-26

### Added

- Show Bocadillo version using `boca -v/-V/--version/version`.
- `boca` is now accessible by running Bocadillo as a module: `python -m bocadillo`.
- `HTTPError` is now available at package level: `from bocadillo import HTTPError`.
- Built-in `HTTPError` handlers: `error_to_html`, `error_to_media`, `error_to_text`.
- `detail` argument to `HTTPError`.
- Startup and shutdown events with `api.on()`.
- Security guide.
- Deployment guide.
- `api.run()` now accepts extra keyword arguments that will be passed to `uvicorn.run()`.
- API reference for all public functionality.

### Changed

- Exceptions raised in middleware callbacks were always handled by the HTML `HTTPError` handler. If configured, the one on the `API` will now be used instead.
- The default `HTTPError` handler now returns plaintext instead of HTML.
- The `static` module was renamed to `staticfiles`.
- The `types` module was renamed to `app_types`.
- The `view` module was renamed to `views`.
- The `routing` package has been flattened into a single `routing` module.

### Fixed

- Serving static files from a non-existing directory (including the default one) used to raise an invasive warning. It has been silenced.

### Removed

- Removed example application.
- Removed dependency on `asgiref` for WSGI sub-apps.

## [v0.7.0] - 2018-12-13

### Added

- Recipes: a way to group stuff together and allow composition of bocadillos.
- Recipe books: a way to group multiple recipes into a single recipe.
- Route namespaces via `namespace` argument to `@api.route()`.
- Add GZip support through `enable_gzip`.
- Add ASGI-compliant middleware support via `api.add_asgi_middleware()`.
- Background tasks via `res.background`.

### Changed

- Exceptions raised in `before_dispatch()` and `after_dispatch()` middleware callbacks will now _always_ lead to 500 error responses — they won't be handled by error handlers anymore, because these are registered on the `API` which middleware only wrap around. The only exception to this is, of course, `HTTPError`.
- All routes now have an inferred `name` based on their function or class name. Explicit route naming is still possible.
- Because of the above, names of routes in recipes now use the recipe's name as a namespace, i.e. `recipe_name:route_name` instead of `route_name`.
- Unsafe HTTP verbs used to be supported by defaults on function-based routes. Only the safe ones, GET and HEAD, are supported by default now.

### Deprecated

- `RoutingMiddleware` has been renamed to `Middleware`. It will still be available as `RoutingMiddleware` until v0.8.

### Fixed

- Errors returned by custom error handlers could have 200 status in case the handler did not set any status code. It now defaults to 500.
- If `GET` is supported, `HEAD` will automatically be implemented.

## [v0.6.1] - 2018-12-04

### Added

- Documentation on the routing algorithm.
- More documentation on how to write views.
- API reference for the `API` class.

### Changed

- Restructure documentation into 4 clear sections: Getting Started, Topics, How-To and API Reference.
- All things related to routing are now in a dedicated `bocadillo.routing` package, which provides a reusable `RoutingMixin`. This does not introduce any API changes.
- Code refactoring for the hooks and templates features. No API changes involved.
- Rewritten `CONTRIBUTING.md`.

## [v0.6.0] - 2018-11-26

### Added

- Route hooks via `@api.before()` and `@api.after()`.
- Media types and media handlers: `API([media_type='application/json'])`, `api.media_type`,
  `api.media_handlers`.
- Support for async callbacks on `RoutingMiddleware`.
- Documentation for the above.
- (Development) Black auto-formatting with pre-commit.
- (Development) Documentation guide in `CONTRIBUTING.md`.

### Changed

- Documentation improvements.

### Fixed

- Exceptions raised inside a middleware callback
  (`before_dispatch()` or `after_dispatch()`) are now properly handled by
  registered error handlers (they were previously left uncaught).
- Middleware callbacks (especially `before_dispatch()`)
  won't be called anymore if the HTTP method is not allowed.

## [v0.5.0] - 2018-11-18

### Added

- Add `boca`, Bocadillo's extensible CLI.
- Add `init:custom` command to generate files for building custom Boca commands.
- Add VuePress-powered documentation site.

### Changed

- Moved docs from README.md to docs site.

## [v0.4.0] - 2018-11-10

### Added

- Named routes. Define a named route by passing a `name` to `@api.route()`. Get the URL path to a route using `api.url_for()` or, in templates, the `url_for()` global.
- Redirections using `api.redirect()`. Can be by route name, internal URL, or external URL. Make it permanent with `permanent=True`.
- Template rendering from string using `api.template_string()`.
- Add allowed hosts configuration through `allowed_host` argument to `API()`.
- _Experimental_ support for routing middleware through `bocadillo.RoutingMiddleware`.
- Add CORS support with restrictive defaults. Enable using `enable_cors = True`, configure through `cors_config`.
- Add HSTS support through `enable_hsts`.

### Changed

- Updated example app to demonstrate usage of redirects and named routes.
- Responses without content do not send an empty JSON object response anymore. Instead, an empty `text/plain` response is sent.
- Responses with 204 status code and no content do not set the `Content-Type` header anymore.

## [v0.3.1] - 2018-11-09

### Fixed

- Fixed mis-configured `setup.py` preventing Bocadillo from being installed from `pip`.

## [v0.3.0] - 2018-11-09

### Added

- Plain text responses using `res.text`.
- HTML responses using `res.html`.
- [Jinja2](http://jinja.pocoo.org)-powered template rendering through `await api.template()` and `api.template_sync()`.
- Mount ASGI or WSGI sub-apps using `app.mount(prefix, sub_app)`.
- Static assets using [WhiteNoise](http://whitenoise.evans.io). Configurable through the `static_root` and `static_dir` arguments to `API()`. By default, the `static` folder is served at `/static`. This can be disabled by passing `static_root = None` to `API()`.
- Register more static files locations by mounting a `bocadillo.static()` sub-app.
- Check (at "compile time") that a) a route pattern begins with a forward slash, and b) all parameters of a route are used on its view and vice-versa.
- Use `text/plain` content type if none was set within a view.

### Changed

- Example app in a dedicated `example/` folder.
- Allow overriding a route by reusing a route pattern. Previously, this would have raised an exception.
- Default static root is now `/static`. It previously defaulted to the static directory, which causes issues if the latter was not a relative path.
- The `res.content` attribute is now for raw response content, and will not set the `text/plain` content type anymore. Allows to send responses of arbitrary content type.
- The default error handler now sends HTML content instead of plain text.

## [v0.2.1] - 2018-11-04

### Added

- Add this `CHANGELOG.md`.
- Add error handling.
- Provide a default HTTP error handler, which catches `HTTPError` exceptions during request processing and returns the appropriate HTTP response.
- Allow to customize error handling through `@api.error_handler()` and `api.add_error_handler()`.
- Allow to restrict HTTP methods supported by a route using the `methods` argument to `@api.route()`. Ignored for class-based views: HTTP methods should be restricted by implementing/not implementing the corresponding method on the class.

### Changed

- Return a `405 Method Not Allowed` response when trying to use a non-implemented method on a class-based view. The previous behavior was to raise an uncaught `ValueError`.
- Updated `example.py`.

### Fixed

- Fixed a bug that prevented routes without parameters to be handled correctly.
- Prevent registering multiple routes on the same pattern.

## v0.1.0 - 2018-11-04

### Added

- The `API` class, an ASGI-compatible application.
- `Request` and `Response` objects, which are wrappers around Starlette's.
- Plain text responses using `res.content`.
- JSON responses through `res.media`.
- Automatic configuration of the response's `Content-Type`: `text/plain` by default, `application/json` if `response.media` was set or `res.content` was left empty.
- Route registration through `@api.route()`.
- Parametrized routes through f-string expressions, e.g. `{my_param}`. Parameters are passed directly to the view, e.g. `my_view(req, resp, my_param)`. Parameters are compliant with the [Literal string interpolation](https://www.python.org/dev/peps/pep-0498/#specification) specification. In particular, type specifiers are supported (e.g. `{age:d}`) which provides basic validation capabilities.
- Class-based views. HTTP methods (GET, POST, PUT, PATCH, DELETE) are mapped to the corresponding lowercase methods on the class, e.g. `.get()`. A generic `.handle()` method can also be given to process any request (other methods will then be ignored).
- Default bind host and port: `127.0.0.1:8000`.
- Automatic host and port based on the `PORT` environment variable. If `PORT` is set, a) the app will bind on that port, b) if no host was specified, the app will bind to known hosts (i.e. `0.0.0.0`).
- `example.py` app.
- `README.md`.
- `CONTRIBUTING.md`.

[unreleased]: https://github.com/bocadilloproject/bocadillo/compare/v0.13.1...HEAD
[v0.13.1]: https://github.com/bocadilloproject/bocadillo/compare/v0.13.0...v0.13.1
[v0.13.0]: https://github.com/bocadilloproject/bocadillo/compare/v0.12.6...v0.13.0
[v0.12.6]: https://github.com/bocadilloproject/bocadillo/compare/v0.12.5...v0.12.6
[v0.12.5]: https://github.com/bocadilloproject/bocadillo/compare/v0.12.4...v0.12.5
[v0.12.4]: https://github.com/bocadilloproject/bocadillo/compare/v0.12.3...v0.12.4
[v0.12.3]: https://github.com/bocadilloproject/bocadillo/compare/v0.12.2...v0.12.3
[v0.12.2]: https://github.com/bocadilloproject/bocadillo/compare/v0.12.1...v0.12.2
[v0.12.1]: https://github.com/bocadilloproject/bocadillo/compare/v0.12.0...v0.12.1
[v0.12.0]: https://github.com/bocadilloproject/bocadillo/compare/v0.11.2...v0.12.0
[v0.11.2]: https://github.com/bocadilloproject/bocadillo/compare/v0.11.1...v0.11.2
[v0.11.1]: https://github.com/bocadilloproject/bocadillo/compare/v0.11.0...v0.11.1
[v0.11.0]: https://github.com/bocadilloproject/bocadillo/compare/v0.10.3...v0.11.0
[v0.10.3]: https://github.com/bocadilloproject/bocadillo/compare/v0.10.2...v0.10.3
[v0.10.2]: https://github.com/bocadilloproject/bocadillo/compare/v0.10.1...v0.10.2
[v0.10.1]: https://github.com/bocadilloproject/bocadillo/compare/v0.10.0...v0.10.1
[v0.10.0]: https://github.com/bocadilloproject/bocadillo/compare/v0.9.1...v0.10.0
[v0.9.1]: https://github.com/bocadilloproject/bocadillo/compare/v0.9.0...v0.9.1
[v0.9.0]: https://github.com/bocadilloproject/bocadillo/compare/v0.8.1...v0.9.0
[v0.8.1]: https://github.com/bocadilloproject/bocadillo/compare/v0.8.0...v0.8.1
[v0.8.0]: https://github.com/bocadilloproject/bocadillo/compare/v0.7.0...v0.8.0
[v0.7.0]: https://github.com/bocadilloproject/bocadillo/compare/v0.6.1...v0.7.0
[v0.6.1]: https://github.com/bocadilloproject/bocadillo/compare/v0.6.0...v0.6.1
[v0.6.0]: https://github.com/bocadilloproject/bocadillo/compare/v0.5.0...v0.6.0
[v0.5.0]: https://github.com/bocadilloproject/bocadillo/compare/v0.4.0...v0.5.0
[v0.4.0]: https://github.com/bocadilloproject/bocadillo/compare/v0.3.1...v0.4.0
[v0.3.1]: https://github.com/bocadilloproject/bocadillo/compare/v0.3.0...v0.3.1
[v0.3.0]: https://github.com/bocadilloproject/bocadillo/compare/v0.2.1.post3...v0.3.0
[v0.2.1]: https://github.com/bocadilloproject/bocadillo/compare/v0.1.0...v0.2.1.post3
