# Changelog

All notable changes to Bocadillo are documented here.

The format of this document is based on [Keep a Changelog](https://keepachangelog.com).

Bocadillo adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

### Added

- HTML responses by setting `response.html`.
- Jinja2-powered template rendering through `api.template()` and `await api.template_async()`.
- Add index route to `example.py` app, which renders an HTML template.

## [v0.2.1]

### Added

- Add this `CHANGELOG.md`.
- Add error handling.
- Provide a default HTTP error handler, which catches `HTTPError` exceptions during request processing and returns the appropriate HTTP response.
- Allow to customize error handling through `@api.error_handler()` and `api.add_error_handler()`.
- Allow to restrict HTTP methods supported by a route using the `methods` argument to `@api.route()`.

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
- Plain text responses through `response.content`.
- JSON responses through `response.media`.
- Automatic configuration of the response's `Content-Type`: `text/plain` by default, `application/json` if `response.media` was set or `response.content` was left empty.
- Route registration through `@api.route()`.
- Parametrized routes through f-string expressions, e.g. `{my_param}`. Parameters are passed directly to the view, e.g. `my_view(req, resp, my_param)`. Parameters are compliant with the [Literal string interpolation](https://www.python.org/dev/peps/pep-0498/#specification) specification. In particular, type specifiers are supported (e.g. `{age:d}`) which provides basic validation capabilities.
- Class-based views. HTTP methods (GET, POST, PUT, PATCH, DELETE) are mapped to the corresponding lowercase methods on the class, e.g. `.get()`. A generic `.handle()` method can also be given to process any request (other methods will then be ignored).
- Default bind host and port: `127.0.0.1:8000`.
- Automatic host and port based on the `PORT` environment variable. If `PORT` is set, a) the app will bind on that port, b) if no host was specified, the app will bind to known hosts (i.e. `0.0.0.0`).
- `example.py` app.
- `README.md`.
- `CONTRIBUTING.md`.

[Unreleased]: https://github.com/florimondmanca/bocadillo/compare/v0.2.1...HEAD
[v0.2.1]: https://github.com/florimondmanca/bocadillo/compare/v0.1.0...v0.2.1.post3
