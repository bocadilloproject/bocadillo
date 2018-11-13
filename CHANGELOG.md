# Changelog

All notable changes to Bocadillo are documented here.

The format of this document is based on [Keep a Changelog](https://keepachangelog.com).

Bocadillo adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

### Added

- Add `boca`, Bocadillo's extensible CLI.
- Add `init:custom` command to generate files for building custom Boca commands.

## [v0.4.0] - 2018-11-10

### Added

- Named routes. Define a named route by passing a `name` to `@api.route()`. Get the URL path to a route using `api.url_for()` or, in templates, the `url_for()` global.
- Redirections using `api.redirect()`. Can be by route name, internal URL, or external URL. Make it permanent with `permanent=True`.
- Template rendering from string using `api.template_string()`.
- Add allowed hosts configuration through `allowed_host` argument to `API()`.
- *Experimental* support for routing middleware through `bocadillo.RoutingMiddleware`.
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

[Unreleased]: https://github.com/florimondmanca/bocadillo/compare/v0.4.0...HEAD
[v0.4.0]: https://github.com/florimondmanca/bocadillo/compare/v0.3.1...v0.4.0
[v0.3.1]: https://github.com/florimondmanca/bocadillo/compare/v0.3.0...v0.3.1
[v0.3.0]: https://github.com/florimondmanca/bocadillo/compare/v0.2.1.post3...v0.3.0
[v0.2.1]: https://github.com/florimondmanca/bocadillo/compare/v0.1.0...v0.2.1.post3
