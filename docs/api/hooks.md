# bocadillo.hooks

## before
```python
before(hook: Callable[[bocadillo.request.Request, bocadillo.response.Response, dict], Awaitable[NoneType]], *args, **kwargs)
```
Register a before hook on a handler.

__Parameters__

- __hook (callable)__: a hook function.

## after
```python
after(hook: Callable[[bocadillo.request.Request, bocadillo.response.Response, dict], Awaitable[NoneType]], *args, **kwargs)
```
Register an after hook on a handler.

__Parameters__

- __hook (callable)__: a hook function.

