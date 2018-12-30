# bocadillo.routing

## RoutingMixin
```python
RoutingMixin(self)
```
Provide routing capabilities to a class.
### route
```python
RoutingMixin.route(self, pattern: str, *, methods: List[str] = None, name: str = None, namespace: str = None)
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

__Raises__

- `RouteDeclarationError`:
    If route validation has failed.

__See Also__

- [check_route](#check-route) for the route validation algorithm.

### url_for
```python
RoutingMixin.url_for(self, name: str, **kwargs) -> str
```
Build the URL path for a named route.

__Parameters__

- __name (str)__: the name of the route.
- __kwargs (dict)__: route parameters.

__Returns__

`url (str)`: the URL path for a route.

__Raises__

- `HTTPError(404) `: if no route exists for the given `name`.

## Route
```python
Route(self, pattern: str, view: Callable[[bocadillo.request.Request, bocadillo.response.Response, dict], Coroutine], methods: List[str], name: str)
```
Represents the binding of an URL pattern to a view.

Note: as a framework user, you will not need to create routes directly.

__Parameters__

- __pattern (str)__: an URL pattern. F-string syntax is supported for parameters.
- __view (coroutine function)__:
    A view given as a coroutine function. Non-async views (synchronous,
    class-based) will have to have been converted beforehand.
- __methods (list of str)__:
    A list of (upper-case) HTTP methods.
- __name (str)__:
    The route's name.

### url
```python
Route.url(self, **kwargs) -> str
```
Return full path for the given route parameters.

__Parameters__

- __kwargs (dict)__: route parameters.

__Returns__

`url (str)`:
    A full URL path obtained by formatting the route pattern with
    the provided route parameters.

### parse
```python
Route.parse(self, path: str) -> Union[dict, NoneType]
```
Parse an URL path against the route's URL pattern.

__Returns__

`result (dict or None)`:
    If the URL path matches the URL pattern, this is a dictionary
    containing the route parameters, otherwise None.

### raise_for_method
```python
Route.raise_for_method(self, req: bocadillo.request.Request)
```
Fail if the requested method is not supported by the route.

__Raises__

- `HTTPError(405)`: if `req.method` is not supported by the route.

## check_route
```python
check_route(pattern: str, view: Union[Callable[[bocadillo.request.Request, bocadillo.response.Response, dict], Coroutine], bocadillo.views.ClassBasedView], methods: List[str]) -> None
```
Check compatibility of a route pattern and a view.

__Parameters__

- __pattern (str)__: an URL pattern.
- __view__: a function-based or class-based view.
- __methods__: an upper-cased list of HTTP methods.

__Raises__

- `RouteDeclarationError `:
    - If one of the `methods` is not a member of `ALL_HTTP_METHODS`.
    - If `pattern` does not have a leading slash.
    - If the `view` does not accept at least two positional arguments
    (for the request and the response objects).
    - If route parameters declared in the pattern do not match those
    used on the view, e.g. a parameter is declared in the pattern, but
    not used in the view or vice-versa.

__See Also__

- `ALL_HTTP_METHODS` is defined in [constants.py](./constants.md).

