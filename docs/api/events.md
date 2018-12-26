# bocadillo.events

## EventsMixin
```python
EventsMixin(self, **kwargs)
```
Allow to register event handlers called during the ASGI lifecycle.
### on
```python
EventsMixin.on(self, event: str, handler: Union[Callable[[], NoneType], NoneType] = None)
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
async def init_app():
    pass
```

### handle_lifespan
```python
EventsMixin.handle_lifespan(self, scope: dict) -> Callable[[Callable, Callable], Coroutine]
```
Create an ASGI application instance to handle `lifespan` messages.

Registered event handlers will be called as appropriate.

__Parameters__

- __scope (dict)__: an ASGI connection scope.

__Returns__

`app (ASGIAppInstance)`: an ASGI application instance.

__See Also__

- [on](#on)
- [Lifespan protocol](https://asgi.readthedocs.io/en/latest/specs/lifespan.html)

