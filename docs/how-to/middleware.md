# Writing middleware

[Middleware] perform operations before and after a request is dispatched.

To write a middleware, create a subclass of `bocadillo.Middleware` and implement `.before_dispatch()` and `.after_dispatch()` as seems fit:

```python
import bocadillo

class PrintUrlMiddleware(bocadillo.Middleware):

    async def before_dispatch(self, req):
        print(req.url)
    
    async def after_dispatch(self, req, res):
        print(res.url)
```

::: tip
The `.before_dispatch()` and `.after_dispatch()` can also be plain, non-`async` Python functions.
:::

You may also override `__init__()` to perform extra initialisation logic.

```python
import bocadillo

class PrintUrlMiddleware(bocadillo.Middleware):
    
    def __init__(self, dispatch, flag=False, **kwargs):
        super().__init__(dispatch, **kwargs)
        # Do stuff based on `flag`
```

Users will be able to register the middleware using `api.add_middleware()`:

```python
api = bocadillo.API()
api.add_middleware(PrintUrlMiddleware, flag=True)
```

[Middleware]: ../topics/features/middleware.md
