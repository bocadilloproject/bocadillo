# bocadillo.routing
This module defines classes (both abstract and concrete) that power routing.

::: tip NOTATIONS
This modules uses the following [generic types]:

- `_T` refers to a route object, i.e. an instance of a subclass of [BaseRoute](#baseroute).
- `_V` refers to a view object.

[generic types]: https://docs.python.org/3/library/typing.html#generics
:::

## BaseRoute
```python
BaseRoute(self, pattern: str, view: ~_V)
```
The base route class.

This is referenced as `_T` in the rest of this module.

__Parameters__

- __pattern (str)__: an URL pattern.
- __view (_V)__:
    a view function or object whose actual type is defined by concrete
    routes.

### url
```python
BaseRoute.url(self, **kwargs) -> str
```
Return the full URL path for the given route parameters.

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
    A mapping of URL patterns to route objects.

### normalize
```python
BaseRouter.normalize(self, view: Any) -> ~_V
```
Perform any conversion necessary to return a proper view object.

This is a no-op by default, i.e. it returns what it's given.

### add_route
```python
BaseRouter.add_route(self, view: ~_V, pattern: str, **kwargs) -> ~_T
```
Register a route (to be implemented by concrete routers).
### route
```python
BaseRouter.route(self, *args, **kwargs) -> Callable[[Any], ~_T]
```
Register a route by decorating a view.

The decorated function or class will be converted to a proper view using
[`.normalize()`](#normalize), and then fed to
[`.add_route()`](#add-route).

__Parameters__

- __*args, **kwargs__:
    passed to [`.add_route()`](#add-route)
    along with the normalized view.

### match
```python
BaseRouter.match(self, path: str) -> Union[bocadillo.routing.RouteMatch[~_T], NoneType]
```
Attempt to match an URL path against one of the registered routes.

__Parameters__

- __path (str)__: an URL path

__Returns__

`match (RouteMatch or None)`:
    a [`RouteMatch`](#routematch) object if the path matched
    a registered route, `None` otherwise.

### mount
```python
BaseRouter.mount(self, other: 'BaseRouter', root: str = '') -> None
```
Mount the routes of another router onto this one.

__Parameters__

- __other (BaseRouter)__:
    should be the same type as this one, i.e.
    [HTTPRouter](#httprouter) or [WebSocketRouter](#websocketrouter).
- __root (str, optional)__:
    will be prefixed to each of `other`'s route pattern.

## HTTPRoute
```python
HTTPRoute(self, pattern: str, view: bocadillo.views.View, name: str)
```
Represents the binding of an URL pattern to an HTTP view.

Subclass of [BaseRoute](#baseroute).

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

Subclass of [BaseRouter](#baserouter).

Note: routes are stored by `name` instead of `pattern`.

### normalize
```python
HTTPRouter.normalize(self, view: Any) -> bocadillo.views.View
```
Build a `View` object.

The input, free-form `view` object is converted using the following
rules:

- Classes are instanciated (without arguments) and converted with
[`from_obj()`][obj].
- Callables are converted with [`from_handler()`][handler].
- Any other object is interpreted as a view-like object, and converted
with [`from_obj()`][obj].

[handler]: ./views.md#from-handler
[obj]: ./views.md#from-obj

__Returns__

`view (View)`:
    a `View` object, ready to be fed to [`.add_route()`](#add-route).

### add_route
```python
HTTPRouter.add_route(self, view: bocadillo.views.View, pattern: str, name: str = None, namespace: str = None, **kwargs) -> bocadillo.routing.HTTPRoute
```
Register an HTTP route.

__Parameters__

- __view (View)__:
    a `View` object. You may use [.normalize()](#normalize-2)
    to get one from a function or class-based view before-hand.
- __pattern (str)__: an URL pattern.
- __name (str)__: a route name (inferred from the view if not given).
- __namespace (str)__: an optional route namespace.

__Returns__

`route (HTTPRoute)`: the registered route.

## WebSocketRoute
```python
WebSocketRoute(self, pattern: str, view: Callable[[bocadillo.websockets.WebSocket], Awaitable[NoneType]], **kwargs)
```
Represents the binding of an URL pattern to a WebSocket view.

Subclass of [BaseRoute](#baseroute).

[WebSocket]: ./websockets.md#websocket

__Parameters__

- __pattern (str)__: an URL pattern.
- __view (coroutine function)__:
    Should take as parameters a `WebSocket` object and
    any extracted route parameters.
- __kwargs (any)__: passed when building the [WebSocket] object.

## WebSocketRouter
```python
WebSocketRouter(self)
```
A router for WebSocket routes.

Subclass of [BaseRouter](#baserouter).

### add_route
```python
WebSocketRouter.add_route(self, view: Callable[[bocadillo.websockets.WebSocket], Awaitable[NoneType]], pattern: str, **kwargs) -> bocadillo.routing.WebSocketRoute
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
Build the full URL path for a named route.

__Parameters__

- __name (str)__: the name of the route.
- __kwargs (dict)__: route parameters.

__Returns__

`url (str)`: an URL path.

__Raises__

- `HTTPError(404) `: if no route exists for the given `name`.

### redirect
```python
RoutingMixin.redirect(self, *, name: str = None, url: str = None, permanent: bool = False, **kwargs)
```
Redirect to another HTTP route.

This is only meant to be used inside an HTTP view.

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

