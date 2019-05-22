# Built-in middleware

This page documents built-in middleware that provide global behavior to Bocadillo applications. To learn more about middleware and how to write your own, see [Middleware](/guide/middleware.md).

## CORS

Bocadillo has built-in support for [Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) (CORS). Adding CORS headers to HTTP responses is typically required when you are building a web service (e.g. a REST API) that web browsers should be able to request directly via AJAX/XHR.

To enable CORS, use the `CORS` setting. Setting it to `True` will enable it with restrictive defaults:

```python
# myproject/settings.py
CORS = True
```

The default CORS configuration is:

- `allow_origins`: none.
- `allow_methods`: `GET`
- `allow_headers`: none.

You'll typically need to customize the CORS configuration to suit your use case, e.g.:

```python
# myproject/settings.py
CORS = {
    "allow_origins": ["app.mysite.com"],
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
```

Please refer to Starlette's [CORSMiddleware](https://www.starlette.io/middleware/#corsmiddleware) documentation for the full list of options and defaults.

## Allowed hosts

By default, a Bocadillo application can run on any host. To specify which hosts are allowed, use the `ALLOWED_HOSTS` setting:

```python
# myproject/settings.py
ALLOWED_HOSTS = ["mysite.com"]
```

If a non-allowed host is used, all requests will return a `400 Bad Request` error.

## HSTS (HTTPS Redirection)

If you want to enable [HTTP Strict Transport Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security) (HSTS) to redirect all HTTP traffic to HTTPS (or WS to WSS), use:

```python
# myproject/settings.py
HSTS = True
```

::: warning
You should only enable HSTS if you have HTTPS configured on your server. See also the [Security: HTTPS](/discussions/security.md#https) guide.
:::

## GZip

If you want to enable [GZip compression](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Encoding#Directives) to compress HTTP responses when possible, use:

```python
# myproject/settings.py
GZIP = True
```

You can also specify the minimum bytes the response should have before compressing:

```python
# myproject/settings.py
GZIP = True
GZIP_MIN_SIZE = 1024  # Default
```
