# bocadillo.views

## View
```python
View(self, name: str, doc: str = None)
```
This class defines how all HTTP views are represented internally.

::: warning
Views objects should not be created directly. Instead, use
[from_handler](#from-handler) or [from_obj](#from-obj).
:::

HTTP methods are mapped to **handlers**, i.e. methods of a `View` object.

The following handlers are supported:

- `.get(req, res, **kwargs)`
- `.post(req, res, **kwargs)`
- `.put(req, res, **kwargs)`
- `.patch(req, res, **kwargs)`
- `.delete(req, res, **kwargs)`
- `.head(req, res, **kwargs)`
- `.options(req, res, **kwargs)`
- `.handle(req, res, **kwargs)`

::: tip
`.handle()` is special: if defined, it overrides all others.
:::

__Attributes__


- `name (str)`: the name of the view.

## from_handler
```python
from_handler(handler: Callable[[bocadillo.request.Request, bocadillo.response.Response, Any], Awaitable[NoneType]], methods: Union[List[str], <built-in function all>] = None) -> bocadillo.views.View
```
Convert a handler to a `View` instance.

__Parameters__

- __handler (function or coroutine function)__:
    Its name and docstring are copied onto the view.
    It used as a handler for each of the declared `methods`.
    For example, if `methods=["post"]` then the returned `view` object
    will only have a `.post()` handler.
- __methods (list of str)__:
    A list of supported HTTP methods. The `all` built-in can be used
    to support all HTTP methods. Defaults to `["get"]`.

__Returns__

`view (View)`: a `View` instance.

__See Also__

- The [constants](./constants.md) module for the list of all HTTP methods.

## from_obj
```python
from_obj(obj: Any) -> bocadillo.views.View
```
Convert an object to a `View` instance.

__Parameters__

- __obj (any)__:
    its handlers, snake-cased class name and docstring are copied
    onto the view.

__Returns__

`view (View)`: a `View` instance.

## get_handlers
```python
get_handlers(obj: Any) -> Dict[str, Callable[[bocadillo.request.Request, bocadillo.response.Response, Any], Awaitable[NoneType]]]
```
Return all `View` handlers declared on an object.

__Parameters__

- __obj (any)__: an object.

__Returns__

`handlers (dict)`:
    A dict mapping an HTTP method to a handler.

## view
```python
view(methods: Union[List[str], <built-in function all>] = None)
```
Convert the decorated function to a proper `View` object.

This decorator is a shortcut for [from_handler](#from-handler).

