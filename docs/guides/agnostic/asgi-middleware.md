# ASGI middleware

ASGI middleware provides global behavior at the earliest stage in the processing of requests. It works in similar ways to [HTTP middleware], but there are also some key differences.

[http middleware]: /guides/http/middleware.md

## Comparison with HTTP middleware

Similarities:

- The same [stack-like processing algorithm](../http/middleware.md#how-http-middleware-is-applied) is used.
- ASGI middleware takes the form of middleware classes, too.

Differences:

- ASGI middleware is **generic**: it works both in the context of HTTP _and_ WebSocket.
- ASGI middleware classes implement the [ASGI] interface directly, which means you can use any third-party ASGI middleware class without extra plumbing.
- ASGI middleware operates before any HTTP middleware (higher priority).

[asgi]: https://asgi.readthedocs.io

## Using ASGI middleware

You can register ASGI middleware classes using `app.add_asgi_middleware()`.

For example, this is how Bocadillo registers the [HSTS](/guides/architecture/app.md#hsts) middleware internally:

```python
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_asgi_middleware(HTTPSRedirectMiddleware)
```

::: tip
Extra keyword arguments passed to `.add_asgi_middleware()` are forwarded to the middleware class when it is instanciated.
:::

If you're interested in writing your own ASGI middleware, see our [Writing middleware](/how-to/middleware.md) how-to guide.
