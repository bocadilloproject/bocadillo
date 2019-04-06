# Applications

The main object you'll manipulate in Bocadillo is the [App] object, an
[ASGI]-compatible application.

[app]: /api/applications.md#app

This page explains the basics of serving and configurating an application.

[asgi]: https://asgi.readthedocs.io

## Serving an application

### Basics

The officially recommended web server for Bocadillo is [uvicorn]. It comes installed with the `bocadillo` package, so you can use it right away.

[uvicorn]: https://www.uvicorn.org

If the application is declared as `app` in the `app.py` script, e.g.:

```python
from bocadillo import App

app = App()
```

you can serve it using:

```bash
uvicorn app:app
```

### Server configuration

You can use any of the [uvicorn settings](https://www.uvicorn.org/settings/) to configure the server.

For example, you can tell uvicorn to use port 5000 using:

```bash
uvicorn app:app --port 5000
```

### Hot reload

Hot reload is baked into uvicorn. Use the uvicorn `--reload` argument and uvicorn will watch your files and automatically reload the whole application on each file change! This is extremely useful in a development setting.

```bash
uvicorn app:app --reload
```

## Configuration

### Allowed hosts

By default, a Bocadillo application can run on any host. To specify which hosts are allowed, use `allowed_hosts`:

```python
app = App(allowed_hosts=['mysite.com'])
```

If a non-allowed host is used, all requests will return a `400 Bad Request` error.

### CORS

Bocadillo has built-in support for [Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) (CORS). Adding CORS headers to HTTP responses is typically required when you are building a web service (e.g. a REST API) that web browsers should be able to request directly via AJAX/XHR.

To enable CORS, simply use:

```python
app = App(enable_cors=True)
```

Bocadillo has restrictive defaults to prevent security issues: empty `Allow-Origins`, only `GET` for `Allow-Methods`, empty `Allow-Headers`.

This means that you'll typically need to customize the CORS configuration. You can do so using `cors_config`, e.g.:

```python
app = App(
    enable_cors=True,
    cors_config={
        "allow_origins": ["*"],
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
)
```

Please refer to Starlette's [CORSMiddleware](https://www.starlette.io/middleware/#corsmiddleware) documentation for the full list of options and defaults.

### HSTS

If you want enable [HTTP Strict Transport Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security) (HSTS) and redirect all HTTP traffic to HTTPS (or WS to WSS), simply use:

```python
app = App(enable_hsts=True)
```

You should only enable HSTS if you have HTTPS configured on your server. See also the [Security: HTTPS] guide.

[security: https]: /discussions/security.md#https

### GZip

If you want to enable [GZip compression](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Encoding#Directives) to compress HTTP responses when possible, simply use:

```python
app = App(enable_gzip=True)
```

You can also specify the minimum bytes the response should have before compressing:

```python
app = App(enable_gzip=True, gzip_min_size=2048)
```
