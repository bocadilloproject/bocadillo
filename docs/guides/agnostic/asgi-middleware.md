# ASGI middleware

ASGI middleware provides global behavior at the earliest stage in the processing of requests. It works in similar ways to [HTTP middleware], but there are also some key differences.

## Comparison with HTTP middleware

Similarities:

- The same [stack-style processing algorithm](../http/middleware.md#how-http-middleware-is-applied) is used.
- ASGI middleware takes the form of middleware classes, too.

Differences:

- ASGI middleware is **generic**; it works both in the context of HTTP _and_ WebSocket.
- ASGI middleware classes implement the [ASGI] interface directly, which means you can use any third-party ASGI middleware class without extra plumbing.
- ASGI middleware operates before any HTTP middleware.

## Using ASGI middleware

You can register ASGI middleware classes using `app.add_asgi_middleware()`.

For example, this is how Bocadillo registers the [HSTS] middleware internally:

```python
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_asgi_middleware(HTTPSRedirectMiddleware)
```

::: tip
Extra keyword arguments passed to `.add_asgi_middleware()` are forwareded to the middleware class when it is instanciated.
:::

## Built-in ASGI middleware

We provide handy usage shortcuts for some built-in ASGI middleware classes.

### CORS

Bocadillo has built-in support for [Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) (CORS). Adding CORS headers to HTTP responses is typically required when you are building a web service (e.g. a REST API) that web browsers should be able to request directly via AJAX/XHR.

To enable CORS, simply use:

```python
app = bocadillo.App(enable_cors=True)
```

Bocadillo has restrictive defaults to prevent security issues: empty `Allow-Origins`, only `GET` for `Allow-Methods`. To customize the CORS configuration, use `cors_config`, e.g.:

```python
app = bocadillo.App(
    enable_cors=True,
    cors_config={
        'allow_origins': ['*'],
        'allow_methods': ['*'],
    }
)
```

Please refer to Starlette's [CORSMiddleware](https://www.starlette.io/middleware/#corsmiddleware) documentation for the full list of options and defaults.

### HSTS

If you want enable [HTTP Strict Transport Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security) (HSTS) and redirect all HTTP traffic to HTTPS (or WS to WSS), simply use:

```python
app = bocadillo.App(enable_hsts=True)
```

You should only enable HSTS if you have HTTPS configured on your server. See also the [Security: HTTPS] guide.

### GZip

If you want to enable [GZip compression](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Encoding#Directives) to compress HTTP responses when possible, simply use:

```python
app = bocadillo.App(enable_gzip=True)
```

You can also specify the minimum bytes the response should have before compressing:

```python
app = bocadillo.App(enable_gzip=True, gzip_min_size=2048)
```

[http middleware]: ../http/middleware.md
[hsts]: #hsts
[asgi]: https://asgi.readthedocs.io
[security: https]: ../../discussions/security.md#https
