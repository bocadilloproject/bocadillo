# API
```python
API(self, templates_dir: str = 'templates', static_dir: Union[str, NoneType] = 'static', static_root: Union[str, NoneType] = 'static', allowed_hosts: List[str] = None, enable_cors: bool = False, cors_config: dict = None, enable_hsts: bool = False, media_type: Union[str, NoneType] = 'application/json')
```
The all-mighty API class.

This class implements the [ASGI](https://asgi.readthedocs.io) protocol.

__Example__


```python
>>> import bocadillo
>>> api = bocadillo.API()
```

__Parameters__


- __templates_dir (str)__:
    The name of the directory where templates are searched for,
    relative to the application entry point.
    Defaults to `'templates'`.
- __static_dir (str)__:
    The name of the directory containing static files, relative to
    the application entry point. Set to `None` to not serve any static
    files.
    Defaults to `'static'`.
- __static_root (str)__:
    The path prefix for static assets.
    Defaults to `'static'`.
- __allowed_hosts (list of str, optional)__:
    A list of hosts which the server is allowed to run at.
    If the list contains `'*'`, any host is allowed.
    Defaults to `['*']`.
- __enable_cors (bool)__:
    If `True`, Cross Origin Resource Sharing will be configured according
    to `cors_config`. Defaults to `False`.
    See also [CORS](../topics/features/cors.md).
- __cors_config (dict)__:
    A dictionary of CORS configuration parameters.
    Defaults to `dict(allow_origins=[], allow_methods=['GET'])`.
- __enable_hsts (bool)__:
    If `True`, enable HSTS (HTTP Strict Transport Security) and automatically
    redirect HTTP traffic to HTTPS.
    Defaults to `False`.
    See also [HSTS](../topics/features/hsts.md).
- __media_type (str)__:
    Determines how values given to `res.media` are serialized.
    Can be one of the supported media types.
    Defaults to `'application/json'`.
    See also [Media](../topics/request-handling/media.md).

__Attributes__


- `media_type (str)`:
    The currently configured media type.
    When setting it to a value outside of built-in or custom media types,
    an `UnsupportedMediaType` exception is raised.
- `media_handlers (dict)`:
    The dictionary of supported media handlers.
    You can access, edit or replace this at will.
- `templates_dir (str)`:
    The absolute path where templates are searched for (built from the
    `templates_dir` parameter).

## before
```python
API.before(self, hook_function: Callable[[starlette.requests.Request, bocadillo.response.Response, dict], Coroutine], *args, **kwargs)
```
Register a before hook on a route.

::: tip NOTE
`@api.before()` should be placed  **above** `@api.route()`
when decorating a view.
:::

__Parameters__

- __hook_function (callable)__: A synchronous or asynchronous function with the signature: `(req, res, params) -> None`.

## after
```python
API.after(self, hook_function: Callable[[starlette.requests.Request, bocadillo.response.Response, dict], Coroutine], *args, **kwargs)
```
Register an after hook on a route.

::: tip NOTE
`@api.after()` should be placed **above** `@api.route()`
when decorating a view.
:::

__Parameters__

- __hook_function (callable)__:            A synchronous or asynchronous function with the signature:
    `(req, res, params) -> None`.

## mount
```python
API.mount(self, prefix: str, app: Union[Callable[[dict], Callable[[Callable, Callable], Coroutine]], Callable[[dict, Callable], List[bytes]]])
```
Mount another WSGI or ASGI app at the given prefix.

__Parameters__

- __prefix (str)__: A path prefix where the app should be mounted, e.g. `'/myapp'`.
- __app__: An object implementing [WSGI](https://wsgi.readthedocs.io) or [ASGI](https://asgi.readthedocs.io) protocol.

## add_error_handler
```python
API.add_error_handler(self, exception_cls: Type[Exception], handler: Callable[[starlette.requests.Request, bocadillo.response.Response, Exception], NoneType])
```
Register a new error handler.

__Parameters__

- __exception_cls (Exception class)__:
    The type of exception that should be handled.
- __handler (callable)__:
    The actual error handler, which is called when an instance of
    `exception_cls` is caught.
    Should accept a `req`, a `res` and an `exc`.

## error_handler
```python
API.error_handler(self, exception_cls: Type[Exception])
```
Register a new error handler (decorator syntax).

__Example__

```python
>>> import bocadillo
>>> api = bocadillo.API()
>>> @api.error_handler(KeyError)
... def on_key_error(req, res, exc):
...     pass  # perhaps set res.content and res.status_code
```

## route
```python
API.route(self, pattern: str, *, methods: List[str] = None, name: str = None)
```
Register a new route by decorating a view.

__Parameters__

- __pattern (str)__:
    An URL pattern given as a format string.
- __methods (list of str)__:
    HTTP methods supported by this route.
    Defaults to all HTTP methods.
    Ignored for class-based views.
- __name (str)__:
    A name for this route, which must be unique.

__Raises__

- `RouteDeclarationError`:
    If any method is not a valid HTTP method,
    if `pattern` defines a parameter that the view does not accept,
    if the view uses a parameter not defined in `pattern`,
    if the `pattern` does not start with `/`,
    or if the view did not accept the `req` and `res` parameters.

__Example__

```python
>>> import bocadillo
>>> api = bocadillo.API()
>>> @api.route('/greet/{person}')
... def greet(req, res, person: str):
...     pass
```

## url_for
```python
API.url_for(self, name: str, **kwargs) -> str
```
Build the URL path for a named route.

__Parameters__

- __name (str)__: the name of the route.
- __kwargs (dict)__: route parameters.

__Returns__

`url (str)`: the URL path for a route.

__Raises__

- `HTTPError(404) `: if no route exists for the given `name`.

## redirect
```python
API.redirect(self, *, name: str = None, url: str = None, permanent: bool = False, **kwargs)
```
Redirect to another route.

__Parameters__

- __name (str)__: name of the route to redirect to.
- __url (str)__: URL of the route to redirect to, required if `name` is ommitted.
- __permanent (bool)__:
    If `False` (the default), returns a temporary redirection (302).
    If `True`, returns a permanent redirection (301).
- __kwargs (dict)__:
    Route parameters.

__Raises__

- `Redirection`: an exception that will be caught by `API.dispatch()`.

## template
```python
API.template(self, name_: str, context: dict = None, **kwargs) -> Coroutine
```
Render a template asynchronously.

Can only be used within `async` functions.

__Parameters__


- __name (str)__:
    Name of the template, located inside `templates_dir`.
    The trailing underscore avoids collisions with a potential
    context variable named `name`.
- __context (dict)__:
    Context variables to inject in the template.
- __kwargs (dict)__:
    Context variables to inject in the template.

## template_sync
```python
API.template_sync(self, name_: str, context: dict = None, **kwargs) -> str
```
Render a template synchronously.

See also: `API.template()`.

## template_string
```python
API.template_string(self, source: str, context: dict = None, **kwargs) -> str
```
Render a template from a string (synchronous).

__Parameters__

- __source (str)__: a template given as a string.

For other parameters, see `API.template()`.

## add_middleware
```python
API.add_middleware(self, middleware_cls, **kwargs)
```
Register a middleware class.

See also [Middleware](../topics/features/middleware.md).

__Parameters__


- __middleware_cls (Middleware class)__:
    It should be a #~some.middleware.RoutingMiddleware class (not an instance!), or any
    concrete subclass or #~some.middleware.Middleware.

## dispatch
```python
API.dispatch(self, request: starlette.requests.Request, before: List[Callable] = None, after: List[Callable] = None) -> bocadillo.response.Response
```
Dispatch a request and return a response.

For the exact algorithm, see
[How are requests processed?](../topics/request-handling/routes-url-design.md#how-are-requests-processed).

__Parameters__

- __request (Request)__: an inbound HTTP request.
- __before (list of callables)__: a list of middleware `before_dispatch` hooks.
- __after (list of callables)__: a list of middleware `after_dispatch` hooks.

__Returns__

`response (Response)`: an HTTP response.

## find_app
```python
API.find_app(self, scope: dict) -> Callable[[Callable, Callable], Coroutine]
```
Return the ASGI application suited to the given ASGI scope.

This is also what `API.__call__(self)` returns.

__Parameters__

- __scope (dict)__:
    An ASGI scope.

__Returns__

`app`:
    An ASGI application instance
    (either `self` or an instance of a sub-app).

## run
```python
API.run(self, host: str = None, port: int = None, debug: bool = False, log_level: str = 'info')
```
Serve the application using [uvicorn](https://www.uvicorn.org).

For further details, refer to
[uvicorn settings](https://www.uvicorn.org/settings/).

__Parameters__


- __host (str)__:
    The host to bind to.
    Defaults to `'127.0.0.1'` (localhost).
    If not given and `$PORT` is set, `'0.0.0.0'` will be used to
    serve to all known hosts.
- __port (int)__:
    The port to bind to.
    Defaults to `8000` or (if set) the value of the `$PORT` environment
    variable.
- __debug (bool)__:
    Whether to serve the application in debug mode. Defaults to `False`.
- __log_level (str)__:
    A logging level for the debug logger. Must be a logging level
    from the `logging` module. Defaults to `'info'`.

