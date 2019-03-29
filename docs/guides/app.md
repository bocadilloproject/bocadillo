# Applications

The main object you'll manipulate in Bocadillo is the [App] object, an
[ASGI]-compatible application.

[app]: /api/applications.md#app

This page explains the basics of running and configurating an application.

[asgi]: https://asgi.readthedocs.io

## Running the application server

### Basics

The Bocadillo server is powered by [uvicorn], a Python ASGI web server installed along with Bocadillo.

Consider the following application:

```python
# app.py
from bocadillo import App

app = App()

if __name__ == '__main__':
    app.run()
```

To start the application server, either:

[uvicorn]: https://www.uvicorn.org

- Run the application script:

```bash
python app.py
```

- Give it to uvicorn as `path.to.module:app_variable`:

```bash
uvicorn app:app
```

### Debug mode

During development, you can run an application in debug mode to enable in-browser tracebacks and hot reloading.

::: danger
Debug mode discloses sensitive information about your application runtime. We strongly recommend to **disable it in production**.
:::

When running via the application script, debug mode can be enabled:

- By setting the `BOCADILLO_DEBUG` environment variable to a non-empty value.

- By passing `debug=True` to `app.run`:

```python
app.run(debug=True)
```

::: warning CAVEAT
In debug mode, for uvicorn to be able to find the application object, you should declare it as `app` in the application script — like we do on this page.

If you can't, you should tell uvicorn by passing the `declared_as` argument:

```python
application.run(debug=True, declared_as="application")
```

:::

Alternatively, you can activate debug mode from the command line by passing the `--debug` flag to uvicorn:

```bash
uvicorn app:app --debug
```

## Configuration

### Host and port

By default, Bocadillo serves your app at `127.0.0.1:8000`,
i.e. `localhost` on port 8000.

To customize the host and port, you can:

- Specify them on `app.run()`:

```python
app.run(host='mydomain.org', port=5045)
```

- Set the `PORT` environment variable. Bocadillo will pick
  it up and automatically use the host `0.0.0.0` to accept all existing hosts
  on the machine. This is especially useful when running the app in a
  container, or if your hosting provider (e.g. Heroku) injects a port via this environment variable. If needed, you can still specify
  the `host` on `app.run()`.

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
