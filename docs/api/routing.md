# bocadillo.routing

## BaseRoute
```python
BaseRoute(self, pattern: str)
```
The base route class.

__Parameters__

- __pattern (str)__: an URL pattern.

### url
```python
BaseRoute.url(self, **kwargs) -> str
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
BaseRoute.parse(self, path: str) -> Union[dict, NoneType]
```
Parse an URL path against the route's URL pattern.

__Returns__

`params (dict or None)`:
    If the URL path matches the URL pattern, this is a dictionary
    containing the route parameters, otherwise it is `None`.

## RouteMatch
```python
RouteMatch(self, route: ~_T, params: dict)
```
Represents a match between an URL path and a route.

__Parameters__

- __route (BaseRoute)__: a route object.
- __params (dict)__: extracted route parameters.

## BaseRouter
```python
BaseRouter(self)
```
The base router class.

__Attributes__

- `routes (dict)`:
    A mapping of patterns to route objects.

### add_route
```python
BaseRouter.add_route(self, *args, **kwargs)
```
Register a route. Not implemented.
### route
```python
BaseRouter.route(self, *args, **kwargs)
```
Register a route by decorating a view.
### match
```python
BaseRouter.match(self, path: str) -> Union[bocadillo.routing.RouteMatch[~_T], NoneType]
```
Attempt to match an URL path against one of the registered routes.

__Parameters__

- __path (str)__: an URL path

__Returns__

`match (RouteMatch or None)`:
    a `RouteMatch` object if the path matched a registered route,
    `None` otherwise.

## HTTPRoute
```python
HTTPRoute(self, pattern: str, view: bocadillo.views.View, name: str)
```
Represents the binding of an URL pattern to an HTTP view.

__Parameters__

- __pattern (str)__: an URL pattern.
- __view (View)__:
    A `View` object.
- __name (str)__:
    The route's name.

## HTTPRouter
```python
HTTPRouter(self)
```
A router for HTTP routes.

Extends [BaseRouter](#baserouter).

Note: routes are stored by `name` instead of `pattern`.

### add_route
```python
HTTPRouter.add_route(self, view: Union[bocadillo.views.View, Type[Any], Callable, Any], pattern: str, *, name: str = None, namespace: str = None) -> bocadillo.routing.HTTPRoute
```
Register an HTTP route.

If the given `view` is not a `View` object, it is converted to one:

- Classes are instanciated (without arguments) and converted with
[from_obj].
- Callables are converted with [from_handler].
- Any other object is interpreted as a view-like object, and converted
with [from_obj].

[from_handler]: /api/views.md#from-handler
[from_obj]: /api/views.md#from-obj

__Parameters__

- __view (View, class, callable, or object)__:
    convertible to `View` (see above).
- __pattern (str)__: an URL pattern.
- __name (str)__: a route name (inferred from the view if not given).
- __namespace (str)__: an optional route namespace.

__Returns__

`route (HTTPRoute)`: the registered route.

## WebSocketRoute
```python
WebSocketRoute(self, pattern: str, view: Callable[[bocadillo.websockets.WebSocket], Awaitable[NoneType]], **kwargs)
```
Represents the binding of an URL path to a WebSocket view.

[WebSocket]: /api/websockets.md#websocket

__Parameters__

- __pattern (str)__: an URL pattern.
- __view (coroutine function)__:
    Should take as parameter a `WebSocket` object and
    any extracted route parameters.
- __kwargs (any)__: passed when building the [WebSocket] object.

## WebSocketRouter
```python
WebSocketRouter(self)
```
A router for WebSocket routes.

Extends [BaseRouter](#baserouter).

### add_route
```python
WebSocketRouter.add_route(self, view: Callable[[bocadillo.websockets.WebSocket], Awaitable[NoneType]], pattern: str, **kwargs)
```
Register a WebSocket route.

__Parameters__

- __pattern (str)__: an URL pattern.
- __view (coroutine function)__: a WebSocket view.

__Returns__

`route (WebSocketRoute)`: the registered route.

## RoutingMixin
```python
RoutingMixin(self, **kwargs)
```
Provide HTTP and WebSocket routing to an application class.
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

__See Also__

- [check_route](#check-route) for the route validation algorithm.

### websocket_route
```python
RoutingMixin.websocket_route(self, pattern: str, *, value_type: Union[str, NoneType] = None, receive_type: Union[str, NoneType] = None, send_type: Union[str, NoneType] = None, caught_close_codes: Union[Tuple[int], NoneType] = None)
```
Register a WebSocket route by decorating a view.

__Parameters__

- __pattern (str)__: an URL pattern.

__See Also__

- [WebSocket](./websockets.md#websocket) for a description of keyword
arguments.

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

### redirect
```python
RoutingMixin.redirect(self, *, name: str = None, url: str = None, permanent: bool = False, **kwargs)
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

