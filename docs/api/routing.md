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

`result (dict or None)`:
    If the URL path matches the URL pattern, this is a dictionary
    containing the route parameters, otherwise None.

## RouteMatch
```python
RouteMatch(self, route: ~_R, params: dict)
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
BaseRouter.match(self, path: str) -> Union[bocadillo.routing.RouteMatch[~_R], NoneType]
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
WebSocketRouter.add_route(self, pattern: str, view: Callable[[bocadillo.websockets.WebSocket], Awaitable[NoneType]], **kwargs)
```
Register a WebSocket route.

__Parameters__

- __pattern (str)__: an URL pattern.
- __view (coroutine function)__: a WebSocket view.

__Returns__

`route (WebSocketRoute)`: the registered route.

