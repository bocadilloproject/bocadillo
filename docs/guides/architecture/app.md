# Applications

The main object you'll manipulate in Bocadillo is the [App] object, an
[ASGI]-compatible application.

[app]: /api/applications.md#app

This page explains the basics of serving and configurating an application.

[asgi]: https://asgi.readthedocs.io

## Serving an application

### Basics

The officially recommended web server for Bocadillo is [uvicorn]. It comes installed with the `bocadillo` package, so you can use it right away!

[uvicorn]: https://www.uvicorn.org

If the application is declared as `app` in the `app.py` script, e.g.:

```python
from bocadillo import App, configure

app = App()
configure(app)
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

Hot reload is baked into uvicorn! 🚀 Use the uvicorn `--reload` argument and uvicorn will watch your files and automatically reload the whole application on each file change! This is extremely useful in a development setting.

```bash
uvicorn app:app --reload
```

## Configuration

### How applications are configured

Configuration is a **required step** before the application can be served by an ASGI server such as uvicorn. It sets up features such as CORS headers, HTTPS redirection or static files which must only be configured on the root application, i.e. the one given to the web server.

::: tip
Configuring an application doesn't do anything on its own: it is only an interface that plugins hook into in order to implement the desired behavior. [Learn more about plugins](/guides/architecture/plugins.md).
:::

### Basic usage

To configure an application, use the `configure()` helper:

```python
from bocadillo import App, configure

# Example app
app = App()

# Configure it!
configure(app)
```

Besides the mandatory `app` argument, `configure()` can be given:

- A settings object from which upper-cased settings are retrieved — most useful with a [settings module](#settings-module)).
- Arbitrary settings passed as keyword arguments — most useful for programmatic usage:

```python
configure(app, allowed_hosts=["example.com"])
```

### Settings module

The recommended way to configure an application is through a **settings module**, i.e. a `.py` file which declares settings as upper-cased constants.

We recommend you use Starlette's [Config helper](https://www.starlette.io/config/): it reads configuration from environment variables by default and also supports `.env` files. This makes it suited for both production and development use cases.

```python
# settings.py
from starlette.config import Config
from starlette.datastructures import URL

config = Config(".env")

DATABASE_URL = config("DATABASE_URL", cast=URL)
```

```python
# app.py
from bocadillo import App, configure
import settings

app = App()
configure(app, settings)
```

### Server entry point

If you expect settings to change at runtime (e.g. to use test-specific values), you can separate application declaration and application configuration by creating a **server entry point**. This entry point is typically named `asgi.py`.

```python
# app.py
from bocadillo import App

app = App()

# Register routes on `app`…
```

```python
# asgi.py
from bocadillo import configure
from app import app
import settings

configure(app, settings)
```

You can then serve the app using `uvicorn asgi:app` (instead of `uvicorn app:app`).

### Retrieving settings

Much in the style of Django, you can access settings anywhere in the application code base using the `settings` helper. It is a lazy object which is populated once `configure()` is called. Besides regular dot notation access, it also exposes a `dict`-like `.get()` method to retrieve a setting with a default value.

```python
from bocadillo import App, settings

app = App()

@app.route("/")
async def index(req, res):
    if settings.get("PUBLIC", False):
        res.text = "Hello, world!"
    else:
        res.text = "Coming soon!"
```

## Built-in features

::: tip
In this section, configuration examples suppose you use a [settings module](#settings-module).
:::

### Allowed hosts

By default, a Bocadillo application can run on any host. To specify which hosts are allowed, use the `ALLOWED_HOSTS` setting:

```python
ALLOWED_HOSTS = ["mysite.com"]
```

If a non-allowed host is used, all requests will return a `400 Bad Request` error.

### CORS

Bocadillo has built-in support for [Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) (CORS). Adding CORS headers to HTTP responses is typically required when you are building a web service (e.g. a REST API) that web browsers should be able to request directly via AJAX/XHR.

To enable CORS with (restrictive) default settings, use the `CORS` setting:

```python
CORS = True
```

The default settings are: empty `Allow-Origins`, only `GET` for `Allow-Methods`, empty `Allow-Headers`. You'll typically need to customize the CORS configuration to suit your use case, e.g.:

```python
CORS = {
    "allow_origins": ["app.mysite.com"],
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
```

Please refer to Starlette's [CORSMiddleware](https://www.starlette.io/middleware/#corsmiddleware) documentation for the full list of options and defaults.

### HSTS

If you want to enable [HTTP Strict Transport Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security) (HSTS) to redirect all HTTP traffic to HTTPS (or WS to WSS), use:

```python
HSTS = True
```

::: warning
You should only enable HSTS if you have HTTPS configured on your server. See also the [Security: HTTPS](/discussions/security.md#https) guide.
:::

### GZip

If you want to enable [GZip compression](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Encoding#Directives) to compress HTTP responses when possible, use:

```python
GZIP = True
```

You can also specify the minimum bytes the response should have before compressing:

```python
GZIP = True
GZIP_MIN_SIZE = 1024  # Default
```
