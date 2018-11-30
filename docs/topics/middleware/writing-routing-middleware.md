# Writing routing middleware

Routing middleware performs operations **before and after a view is executed**.

To write a routing middleware, create a subclass of `bocadillo.RoutingMiddleware` and implement `.before_dispatch()` and `.after_dispatch()` as seems fit:

```python
import bocadillo

class PrintUrlMiddleware(bocadillo.RoutingMiddleware):

    async def before_dispatch(self, req):
        print(req.url)
    
    async def after_dispatch(self, req, res):
        print(res.url)
```

::: tip
- The `.before_dispatch()` and `.after_dispatch()` can also be plain, non-`async` Python functions.
- The underlying application (which is either another routing middleware or the `API` object) is available on the `.app` attribute.
:::

You can then register the middleware using `api.add_middleware()`:

```python
api = bocadillo.API()
api.add_middleware(PrintUrlMiddleware)
```
