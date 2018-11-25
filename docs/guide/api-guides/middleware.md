# Middleware

::: warning
This feature is **experimental**; the middleware API may be subject to changes.
:::

Bocadillo provides a simple middleware architecture in the form of middleware classes.

Middleware classes provide behavior for the entire application. They act as an intermediate between the ASGI layer and the Bocadillo API object. In fact, they implement the ASGI protocol themselves.

## Routing middleware

Routing middleware performs operations before and after a request is routed to the Bocadillo application.

To define a custom routing middleware class, create a subclass of `bocadillo.RoutingMiddleware` and implement `.before_dispatch()` and `.after_dispatch()` as necessary:

```python
import bocadillo

class PrintUrlMiddleware(bocadillo.RoutingMiddleware):

    def before_dispatch(self, req):
        print(req.url)
    
    def after_dispatch(self, req, res):
        print(res.url)
```

::: tip
The `.before_dispatch()` and `.after_dispatch()` can be `async`. Use this when, for example, accessing the request's body.
:::

::: tip
The underlying application (which is either another routing middleware or the `API` object) is available on the `.app` attribute.
:::

You can then register the middleware using `add_middleware()`:

```python
api = bocadillo.API()
api.add_middleware(PrintUrlMiddleware)
```
