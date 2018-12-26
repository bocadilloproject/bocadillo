# bocadillo.hooks

## HooksBase
```python
HooksBase(self, /, *args, **kwargs)
```
Base class for hooks managers.

When subclassing:

- `__route_class__` should be defined.
- `store_hook()` should be implemented.

### store_hook
```python
HooksBase.store_hook(self, hook: str, hook_function: Callable[[bocadillo.request.Request, bocadillo.response.Response, dict], Coroutine], route: bocadillo.routing.route.Route)
```
Store a hook function for a route.

The implementation must be defined by subclasses.

__Parameters__


- __hook (str)__:
    The name of the hook.
- __hook_function (HookFunction)__:
    A hook function.
- __route (Route)__:
    A route object.

## Hooks
```python
Hooks(self)
```
A concrete hooks manager that stores hooks by route.
### on
```python
Hooks.on(self, route: bocadillo.routing.route.Route, req: bocadillo.request.Request, res: bocadillo.response.Response, params: dict)
```
Execute `before` hooks on enter and `after` hooks on exit.
## HooksMixin
```python
HooksMixin(self)
```
Mixin that provides hooks to application classes.
### before
```python
HooksMixin.before(self, hook_function: Callable[[bocadillo.request.Request, bocadillo.response.Response, dict], Coroutine], *args, **kwargs)
```
Register a before hook on a route.

::: tip NOTE
`@api.before()` should be placed  **above** `@api.route()`
when decorating a view.
:::

__Parameters__

- __hook_function (callable)__:            A synchronous or asynchronous function with the signature:
    `(req, res, params) -> None`.

### after
```python
HooksMixin.after(self, hook_function: Callable[[bocadillo.request.Request, bocadillo.response.Response, dict], Coroutine], *args, **kwargs)
```
Register an after hook on a route.

::: tip NOTE
`@api.after()` should be placed **above** `@api.route()`
when decorating a view.
:::

__Parameters__

- __hook_function (callable)__:            A synchronous or asynchronous function with the signature:
    `(req, res, params) -> None`.

