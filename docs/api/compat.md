# bocadillo.compat

## call_async
```python
call_async(func: Callable, *args, sync=None, **kwargs) -> Coroutine
```
Call a function in an async manner.

__Parameters__

- __func (Callable)__:
    a callable that is either awaited (if a coroutine function)
    or run in the thread pool (if a regular function).
- __sync (bool)__:
    A hint as to whether `func` is synchronous. If not given, it is
    inferred as `asyncio.iscoroutinefunction(func)`.

__See Also__

- [Executing code in thread or process pools](https://docs.python.org/3/library/asyncio-eventloop.html#executing-code-in-thread-or-process-pools)

## camel_to_snake
```python
camel_to_snake(name: str) -> str
```
Convert a `CamelCase` name to its `snake_case` version.
## empty_wsgi_app
```python
empty_wsgi_app() -> Callable[[dict, Callable[[str, List[str]], NoneType]], List[bytes]]
```
Return a WSGI app that always returns 404 Not Found.
