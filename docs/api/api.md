# API
```python
API(self, templates_dir: str = 'templates', static_dir: Union[str, NoneType] = 'static', static_root: Union[str, NoneType] = 'static', allowed_hosts: List[str] = None, enable_cors: bool = False, cors_config: dict = None, enable_hsts: bool = False, enable_gzip: bool = False, gzip_min_size: int = 1024, media_type: Union[str, NoneType] = 'application/json')
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
    Defaults to `"templates"`.
- __static_dir (str)__:
    The name of the directory containing static files, relative to
    the application entry point. Set to `None` to not serve any static
    files.
    Defaults to `"static"`.
- __static_root (str)__:
    The path prefix for static assets.
    Defaults to `"static"`.
- __allowed_hosts (list of str, optional)__:
    A list of hosts which the server is allowed to run at.
    If the list contains `"*"`, any host is allowed.
    Defaults to `["*"]`.
- __enable_cors (bool)__:
    If `True`, Cross Origin Resource Sharing will be configured according
    to `cors_config`. Defaults to `False`.
    See also [CORS](../topics/features/cors.md).
- __cors_config (dict)__:
    A dictionary of CORS configuration parameters.
    Defaults to `dict(allow_origins=[], allow_methods=["GET"])`.
- __enable_hsts (bool)__:
    If `True`, enable HSTS (HTTP Strict Transport Security) and automatically
    redirect HTTP traffic to HTTPS.
    Defaults to `False`.
    See also [HSTS](../topics/features/hsts.md).
- __enable_gzip (bool)__:
    If `True`, enable GZip compression and automatically
    compress responses for clients that support it.
    Defaults to `False`.
    See also [GZip](../topics/features/gzip.md).
- __gzip_min_size (int)__:
    If specified, compress only responses that
    have more bytes than the specified value.
    Defaults to `1024`.
- __media_type (str)__:
    Determines how values given to `res.media` are serialized.
    Can be one of the supported media types.
    Defaults to `"application/json"`.
    See also [Media](../topics/request-handling/media.md).

## media_handlers
The dictionary of supported media handlers.

You can access, edit or replace this at will.

## media_type
The currently configured media type.

When setting it to a value outside of built-in or custom media types,
an `UnsupportedMediaType` exception is raised.

## templates_dir
The path where templates are searched for, or `None` if not set.

This is built from the `templates_dir` parameter.

## route
```python
API.route(self, pattern: str, *, methods: List[str] = None, name: str = None, namespace: str = None)
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
    A name for this route, which must be unique. Defaults to
    a name based on the view.
- __namespace (str)__:
    A namespace for this route (optional).
    If given, will be prefixed to the `name` and separated by a colon,
- __e.g. `"blog__:index"`.

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
>>> @api.route("/greet/{person}")
... def greet(req, res, person: str):
...     pass
```

## on
```python
API.on(self, event: str, handler: Union[Callable[[], NoneType], NoneType] = None)
```
Register an event handler.

__Parameters__

- __event (str)__:
    Either "startup" (when the server boots) or "shutdown" (when the
    server stops).
- __handler (callback, optional)__:
    The event handler. If not given, this should be used as a
    decorator.

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

- __hook_function (callable)__:            A synchronous or asynchronous function with the signature:
    `(req, res, params) -> None`.

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

## get_template_globals
```python
API.get_template_globals(self)
```
Return global variables available to all templates.

__Returns__

`variables (dict)`: a mapping of variable names to their values.

## mount
```python
API.mount(self, prefix: str, app: Union[Callable[[dict], Callable[[Callable, Callable], Coroutine]], Callable[[dict, Callable], List[bytes]]])
```
Mount another WSGI or ASGI app at the given prefix.

__Parameters__

- __prefix (str)__: A path prefix where the app should be mounted, e.g. `"/myapp"`.
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

## redirect
```python
API.redirect(self, *, name: str = None, url: str = None, permanent: bool = False, **kwargs)
```
Redirect to another route.

__Parameters__

- __name (str)__: name of the route to redirect to.
- __url (str)__: URL of the route to redirect to, required if `name` is omitted.
- __permanent (bool)__:
    If `False` (the default), returns a temporary redirection (302).
    If `True`, returns a permanent redirection (301).
- __kwargs (dict)__:
    Route parameters.

__Raises__

- `Redirection`: an exception that will be caught by `API.dispatch()`.

__See Also__

- [Redirecting](../topics/request-handling/redirecting.md)

## add_middleware
```python
API.add_middleware(self, middleware_cls, **kwargs)
```
Register a middleware class.

__Parameters__


- __middleware_cls (Middleware class)__:
    A subclass of `bocadillo.Middleware`.

__See Also__

- [Middleware](../topics/features/middleware.md)

## add_asgi_middleware
```python
API.add_asgi_middleware(self, middleware_cls, *args, **kwargs)
```
Register an ASGI middleware class.

__Parameters__

- __middleware_cls (Middleware class)__:
    A class that complies with the ASGI specification.

__See Also__

- [Middleware](../topics/features/middleware.md)
- [ASGI](https://asgi.readthedocs.io)

## apply_asgi_middleware
```python
API.apply_asgi_middleware(self, app: Callable[[dict], Callable[[Callable, Callable], Coroutine]]) -> Callable[[dict], Callable[[Callable, Callable], Coroutine]]
```
Wrap the registered ASGI middleware around an ASGI app.

__Parameters__

- __app (ASGIApp)__: a callable complying with the ASGI specification.

__Returns__

`app_with_asgi_middleware (ASGIApp)`:
    The result `app = asgi(app, *args, **kwargs)` for
    each ASGI middleware class.

__See Also__

- [add_asgi_middleware](#add-asgi-middleware)

## dispatch
```python
API.dispatch(self, req: starlette.requests.Request) -> bocadillo.response.Response
```
Dispatch a request and return a response.

__Parameters__

- __req (Request)__: an inbound HTTP request.

__Returns__

`response (Response)`: an HTTP response.

__See Also__

- [How are requests processed?](../topics/request-handling/routes-url-design.md#how-are-requests-processed) for the dispatch algorithm.

## get_response
```python
API.get_response(self, req: starlette.requests.Request) -> bocadillo.response.Response
```
Return a response for an incoming request.

__Parameters__

- __req (Request)__: a Request object.

__Returns__

`res (Response)`:
    a Response object, obtained by going down the middleware chain,
    calling `dispatch()` and going up the middleware chain.

__See Also__

- [dispatch](#dispatch)
- [Middleware](../topics/features/middleware.md)

## app
```python
API.app(self, scope: dict) -> Callable[[Callable, Callable], Coroutine]
```
Build and return an isntance of the `API`'s own ASGI application.

__Parameters__

- __scope (dict)__: an ASGI connection scope.

__Returns__

`asgi (ASGIAppInstance)`:
    creates a `Request` and awaits the result of `get_response()`.

## find_app
```python
API.find_app(self, scope: dict) -> Callable[[Callable, Callable], Coroutine]
```
Return the ASGI application suited to the given ASGI scope.

The application is chosen according to the following algorithm:

- If `scope` has a `lifespan` type, the lifespan handler is returned.
This occurs on server startup and shutdown.
- If the scope's `path` begins with any of the prefixes of a mounted
sub-app, said sub-app is returned (converting from WSGI to ASGI if
necessary).
- Otherwise, the API's application is returned.

__Parameters__

- __scope (dict)__:
    An ASGI scope.

__Returns__

`app`:
    An ASGI application instance.

__See Also__

- [Lifespan Protocol](https://asgi.readthedocs.io/en/latest/specs/lifespan.html)
- [ASGI connection scope](https://asgi.readthedocs.io/en/latest/specs/main.html#connection-scope)
- [Events](../topics/features/events.md)
- [mount](#mount)

## run
```python
API.run(self, host: str = None, port: int = None, debug: bool = False, log_level: str = 'info', _run: Callable = <function run at 0x101a33620>, **kwargs)
```
Serve the application using [uvicorn](https://www.uvicorn.org).

__Parameters__


- __host (str)__:
    The host to bind to.
    Defaults to `"127.0.0.1"` (localhost).
    If not given and `$PORT` is set, `"0.0.0.0"` will be used to
    serve to all known hosts.
- __port (int)__:
    The port to bind to.
    Defaults to `8000` or (if set) the value of the `$PORT` environment
    variable.
- __debug (bool)__:
    Whether to serve the application in debug mode. Defaults to `False`.
- __log_level (str)__:
    A logging level for the debug logger. Must be a logging level
    from the `logging` module. Defaults to `"info"`.
- __kwargs (dict)__:
    Extra keyword arguments that will be passed to the Uvicorn runner.

__See Also__

- [Configuring host and port](../topics/api.md#configuring-host-and-port)
- [Debug mode](../topics/api.md#debug-mode)
- [Uvicorn settings](https://www.uvicorn.org/settings/) for all
available keyword arguments.

