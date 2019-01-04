# bocadillo.middleware

## Middleware
```python
Middleware(self, app: Callable[[bocadillo.request.Request, bocadillo.response.Response], Awaitable[NoneType]], **kwargs)
```
Base class for middleware classes.

__Parameters__

- __dispatch (coroutine function)__:
    a function whose return value can be awaited to obtain a response.
- __kwargs (dict)__:
    Keyword arguments passed when registering the middleware.

### before_dispatch
```python
Middleware.before_dispatch(self, req: bocadillo.request.Request, res: bocadillo.response.Response) -> Union[bocadillo.response.Response, NoneType]
```
Perform processing before a request is dispatched.

If the `Response` object is returned, it will be used
and no further processing will be performed.

__Parameters__

- __req (Request)__: a Request object.
- __res (Response)__: a Response object.

### after_dispatch
```python
Middleware.after_dispatch(self, req: bocadillo.request.Request, res: bocadillo.response.Response) -> Union[bocadillo.response.Response, NoneType]
```
Perform processing after a request has been dispatched.

If the `Response` object is returned, it is used instead of the response
obtained by awaiting `dispatch()`.

__Parameters__

- __req (Request)__: a Request object.
- __res (Response)__: a Response object.

### process
```python
Middleware.process(self, req: bocadillo.request.Request, res: bocadillo.response.Response)
```
Process an incoming request.

Roughly equivalent to:

```python
res = await self.before_dispatch(req) or None
res = res or await self.dispatch(req)
res = await self.after_dispatch(req, res) or res
return res
```

Aliased by `__call__()`.

__Parameters__

- __req (Request)__: a request object.

__Returns__

`res (Response)`: a Response object.

