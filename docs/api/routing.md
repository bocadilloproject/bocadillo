# bocadillo.routing

## RoutingMixin
```python
RoutingMixin(self)
```
Provide routing capabilities to a class.
### route
```python
RoutingMixin.route(self, pattern: str, *, name: str = None, namespace: str = None)
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
Route(self, pattern: str, view: bocadillo.views.View, name: str)
```
Represents the binding of an URL pattern to a view.

Note: as a framework user, you will not need to create routes directly.

__Parameters__

- __pattern (str)__: an URL pattern. F-string syntax is supported for parameters.
- __view (View)__:
    A `View` object.
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

## check_route
```python
check_route(pattern: str, view: bocadillo.views.View) -> None
```
Check compatibility of a route pattern and a view.

__Parameters__

- __pattern (str)__: an URL pattern.
- __view (View)__: a `View` object.

__Raises__

- `RouteDeclarationError `:
    - If `pattern` does not have a leading slash.
    - If route parameters declared in the pattern do not match those
    of any view handler, e.g. a parameter is declared in the pattern, but
    not used in the handler or vice-versa.

__See Also__

- `ALL_HTTP_METHODS` is defined in [constants.py](./constants.md).

