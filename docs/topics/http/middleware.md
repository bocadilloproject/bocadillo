# Middleware

::: warning
This feature is **experimental**; the middleware API may be subject to changes.
:::

The middleware framework is a lightweight, rather low-level system to plug into the processing of requests and responses. Middleware classes provide behavior for the entire Bocadillo application and alter the inputs and outputs globally.

Each middleware is responsible for one specific functionality. For example, the built-in [CORS] middleware provides CORS headers for AJAX requests made by web browsers.

## How middleware is applied

Middleware is applied in a stack-like manner. A middleware is given the request from the middleware above it, processes it (`before_dispatch()` hook), gets a response from the middleware beneath, processes it too (`after_dispatch()` hook) and returns it (i.e. to the middleware above).

Because of this, middleware effectively chain the responsibility of dispatching the request down to the router of the API object, resulting in a chain of callbacks similar to:

```
M1.before_dispatch(req)
    M2.before_dispatch(req)
        ...
            Mn.before_dispatch(req)
                res = api.dispatch(req)
            Mn.after_dispatch(req, res)
        ...
    M2.after_dispatch(res)
M1.after_dispatch(res)
```

## Using middleware

Middleware comes in 2 flavors: regular middleware (subclasses of `bocadillo.Middleware`) and ASGI middleware (which implement the [ASGI] interface).

### Regular middleware

These middleware classes are to be registered by calling `api.add_middleware()`:

```python
api.add_middleware(SomeMiddleware, foo='bar')
```

All keyword arguments passed to `add_middleware()` will be passed to the middleware constructor upon startup.

::: tip NOTE
Middleware are called in reverse order of registration. For example, calling `.add_middleware(M2)` and then `.add_middleware(M1)` will result in `M1` getting its request from `M2`. You can think of this as *wrapping* around the previous middleware. This won't matter most of the times though, as middleware are designed to be as independent as possible from one another.
:::

### ASGI middleware

ASGI middleware are lower-level — they are classes that implement the [ASGI] interface directly. Due to this, they have higher priority in the middleware processing stack than regular middleware.

To use an ASGI middleware, use `api.add_asgi_middleware()` instead.

For example, this is how Bocadillo registers the [HSTS] middleware internally:

```python
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

api.add_asgi_middleware(HTTPSRedirectMiddleware)
```

## Built-in middleware

### CORS

Bocadillo has built-in support for [Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) (CORS). Adding CORS headers to responses is typically required when your API is to be accessed by web browsers.

To enable CORS, simply use:

```python
api = bocadillo.API(enable_cors=True)
```

Bocadillo has restrictive defaults to prevent security issues: empty `Allow-Origins`, only `GET` for `Allow-Methods`. To customize the CORS configuration, use `cors_config`, e.g.:

```python
api = bocadillo.API(
    enable_cors=True,
    cors_config={
        'allow_origins': ['*'],
        'allow_methods': ['*'],
    }
)
```

Please refer to Starlette's [CORSMiddleware](https://www.starlette.io/middleware/#corsmiddleware) documentation for the full list of options and defaults.

### HSTS

If you want enable [HTTP Strict Transport Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security) (HSTS) and redirect all HTTP traffic to HTTPS, simply use:

```python
api = bocadillo.API(enable_hsts=True)
```

### GZip

If you want to enable [GZip compression](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Encoding#Directives) to compress responses when possible, simply use:

```python
api = bocadillo.API(enable_gzip=True)
```

You can also specify the minimum bytes the response should have before compressing:

```python
api = bocadillo.API(enable_gzip=True, gzip_min_size=2048)
```

## Writing middleware

If you're interested in writing your own middleware, see our [Writing middleware] how-to guide.

[CORS]: ./middleware.md#cors
[Writing middleware]: ../../how-to/middleware.md
[ASGI]: https://asgi.readthedocs.io
[HSTS]: ./middleware.md#hsts
