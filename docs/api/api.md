# bocadillo.api

## API
```python
API(self, templates_dir: Union[str, NoneType] = 'templates', static_dir: Union[str, NoneType] = 'static', static_root: Union[str, NoneType] = 'static', allowed_hosts: List[str] = None, enable_cors: bool = False, cors_config: dict = None, enable_hsts: bool = False, enable_gzip: bool = False, gzip_min_size: int = 1024, media_type: str = 'application/json')
```
The all-mighty API class.

This class implements the [ASGI](https://asgi.readthedocs.io) protocol.

__Example__


```python
>>> import bocadillo
>>> api = bocadillo.API()
```

__Parameters__


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
    See also [CORS](../guides/http/middleware.md#cors).
- __cors_config (dict)__:
    A dictionary of CORS configuration parameters.
    Defaults to `dict(allow_origins=[], allow_methods=["GET"])`.
- __enable_hsts (bool)__:
    If `True`, enable HSTS (HTTP Strict Transport Security) and automatically
    redirect HTTP traffic to HTTPS.
    Defaults to `False`.
    See also [HSTS](../guides/http/middleware.md#hsts).
- __enable_gzip (bool)__:
    If `True`, enable GZip compression and automatically
    compress responses for clients that support it.
    Defaults to `False`.
    See also [GZip](../guides/http/middleware.md#gzip).
- __gzip_min_size (int)__:
    If specified, compress only responses that
    have more bytes than the specified value.
    Defaults to `1024`.
- __media_type (str)__:
    Determines how values given to `res.media` are serialized.
    Can be one of the supported media types.
    Defaults to `"application/json"`.
    See also [Media](../guides/http/media.md).

__Attributes__

- `media_handlers (dict)`:
    The dictionary of media handlers.
    You can access, edit or replace this at will.

### media_type
The media type configured when instanciating the application.
### mount
```python
API.mount(self, prefix: str, app: Union[Callable[[dict], Callable[[Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], NoneType]], Awaitable[NoneType]]], Callable[[dict, Callable[[str, List[str]], NoneType]], List[bytes]]])
```
Mount another WSGI or ASGI app at the given prefix.

__Parameters__

- __prefix (str)__: A path prefix where the app should be mounted, e.g. `"/myapp"`.
- __app__: An object implementing [WSGI](https://wsgi.readthedocs.io) or [ASGI](https://asgi.readthedocs.io) protocol.

### recipe
```python
API.recipe(self, recipe: bocadillo.recipes.RecipeBase)
```
Apply a recipe.

__Parameters__

- __recipe (Recipe or RecipeBook)__: a recipe to be applied to the API.

__See Also__

- [Recipes](../guides/agnostic/recipes.md)

### add_error_handler
```python
API.add_error_handler(self, exception_cls: Type[Exception], handler: Callable[[bocadillo.request.Request, bocadillo.response.Response, Exception], Awaitable[NoneType]])
```
Register a new error handler.

__Parameters__

- __exception_cls (Exception class)__:
    The type of exception that should be handled.
- __handler (callable)__:
    The actual error handler, which is called when an instance of
    `exception_cls` is caught.
    Should accept a request, response and exception parameters.

### error_handler
```python
API.error_handler(self, exception_cls: Type[Exception])
```
Register a new error handler (decorator syntax).

__See Also__

- [add_error_handler](#add-error-handler)

### add_middleware
```python
API.add_middleware(self, middleware_cls, **kwargs)
```
Register a middleware class.

__Parameters__


- __middleware_cls (Middleware class)__:
    A subclass of `bocadillo.Middleware`.

__See Also__

- [Middleware](../guides/http/middleware.md)

### add_asgi_middleware
```python
API.add_asgi_middleware(self, middleware_cls, *args, **kwargs)
```
Register an ASGI middleware class.

__Parameters__

- __middleware_cls (Middleware class)__:
    A class that complies with the ASGI specification.

__See Also__

- [ASGI middleware](../guides/agnostic/asgi-middleware.md)
- [ASGI](https://asgi.readthedocs.io)

### on
```python
API.on(self, event: str, handler: Union[Callable[[], Awaitable[NoneType]], NoneType] = None)
```
Register an event handler.

__Parameters__

- __event (str)__:
    Either `"startup"` (when the server boots) or `"shutdown"`
    (when the server stops).
- __handler (callback, optional)__:
    The event handler. If not given, this should be used as a
    decorator.

__Example__


```python
@api.on("startup")
async def startup():
    pass

async def shutdown():
    pass

api.on("shutdown", shutdown)
```

### route
```python
API.route(self, pattern: str, *, name: str = None, namespace: str = None)
```
Register a new route by decorating a view.

__Parameters__

- __pattern (str)__: an URL pattern.
- __methods (list of str)__:
    An optional list of HTTP methods.
    Defaults to `["get", "head"]`.
    Ignored for class-based views.
- __name (str)__:
    An optional name for the route.
    If a route already exists for this name, it is replaced.
    Defaults to a snake-cased version of the view's name.
- __namespace (str)__:
    An optional namespace for the route. If given, it is prefixed to
    the name and separated by a colon.

__See Also__

- [check_route](#check-route) for the route validation algorithm.

### run
```python
API.run(self, host: str = None, port: int = None, debug: bool = False, log_level: str = 'info', _run: Callable = None, **kwargs)
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

- [Configuring host and port](../guides/api.md#configuring-host-and-port)
- [Debug mode](../guides/api.md#debug-mode)
- [Uvicorn settings](https://www.uvicorn.org/settings/) for all
available keyword arguments.

### websocket_route
```python
API.websocket_route(self, pattern: str, *, value_type: Union[str, NoneType] = None, receive_type: Union[str, NoneType] = None, send_type: Union[str, NoneType] = None, caught_close_codes: Union[Tuple[int], NoneType] = None)
```
Register a WebSocket route by decorating a view.

__Parameters__

- __pattern (str)__: an URL pattern.

__See Also__

- [WebSocket](./websockets.md#websocket) for a description of keyword
arguments.

### url_for
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

### redirect
```python
API.redirect(self, *, name: str = None, url: str = None, permanent: bool = False, **kwargs)
```
Redirect to another HTTP route.

__Parameters__

- __name (str)__: name of the route to redirect to.
- __url (str)__:
    URL of the route to redirect to (required if `name` is omitted).
- __permanent (bool)__:
    If `False` (the default), returns a temporary redirection (302).
    If `True`, returns a permanent redirection (301).
- __kwargs (dict)__:
    Route parameters.

__Raises__

- `Redirection`:
    an exception that will be caught to trigger a redirection.

__See Also__

- [Redirecting](../guides/http/redirecting.md)

