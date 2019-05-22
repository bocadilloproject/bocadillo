# Configuration

Configuration is a **required step** before the application can be served by an ASGI server such as uvicorn.

::: tip
Except for [Retrieving settings](#retrieving-settings), you can safely ignore this section if you generated your project using the [Bocadillo CLI](https://github.com/bocadilloproject/bocadillo-cli), which should have set up a [settings module](#settings-module) and a [server entry point](#server-entry-point) for you.
:::

## Configuring applications

Configuration occurs when the `configure()` helper is called with the `app` that should be served. This has the effect of calling all registered [plugins](/guide/plugins.md), which in turn set up features such as CORS, HTTPS redirection, etc.

::: tip NOTE
Since it prepares the `app` for serving, `configure()` can only be called once.
:::

Besides the mandatory `app` argument, `configure()` can be given one or both of the following:

- A settings object or module, e.g. `configure(app, settings)`. In this case, individual settings are obtained from upper-cased constants, e.g. `ALLOWED_HOSTS = ["example.com"]`.

::: tip
You can prevent Bocadillo from treating intermediary variables as settings by prefixing them with a leading underscore, e.g. `_some_var` or `_SOME_VAR`.
:::

- Arbitrary settings passed as keyword arguments, e.g. `configure(app, ALLOWED_HOSTS=["example.com"])`.

## Retrieving settings

If you ever need to access settings at runtime, you can use the `settings` object.

This object can be imported from the `bocadillo` package, and gets populated once `configure()` is called (which has a few gotchas — see warning below). Besides regular dot notation, you can use the dict-like `.get()` method to retrieve a setting with an optional default value.

::: warning
Accessing an attribute of `settings` before `configure()` was called will raise an error.

For this reason, you should only access settings **inside a function or a method**. In other words, you should not access settings at the top level of a Python module.
:::

Here is an example:

```python
# myproject/app.py
from bocadillo import App, settings

app = App()

@app.route("/")
async def index(req, res):
    if settings.get("PUBLIC", False):
        res.text = "Hello, world!"
    else:
        res.text = "Coming soon!"
```

Accessing settings is typically needed when implementing [plugins](/guide/plugins.md).

## Settings module

The recommended way to define configuration is through a **settings module**, i.e. a `.py` file which declares settings as upper-cased constants.

We recommend you use Starlette's [Config helper](https://www.starlette.io/config/) to define settings. It reads configuration from environment variables and also supports `.env` files located at the project root directory. This way, you only need **one settings module** for all environments (production, local development, etc.).

Here's an example:

```python
# myproject/settings.py
from starlette.config import Config

config = Config(".env")

ALLOWED_HOSTS = ["localhost", "example.com"]
HSTS = config("HSTS", default=False)
```

And the corresponding `app.py`

```python
# myproject/app.py
from bocadillo import App, configure
from . import settings

app = App()
configure(app, settings)
```

::: warning
The `from . import settings` statement above is a **relative import**. It only works if the code is located inside a **package** — here, `myproject`. If you don't use a package, you will need to use absolute imports, e.g. `import settings`.

For more information on Python imports, see [Absolute vs Relative Imports In Python](https://realpython.com/absolute-vs-relative-python-imports/) (Real Python).
:::

## Server entry point

Although the [minimal working app](/guide/apps.md#minimal-working-app) instanciates and configures the `app` within the same script, it is recommended to perform these operations separately. This allows you to change settings at runtime, and encourages more decoupling between settings and applications.

To achieve this, you should create a **server entry point**, i.e. a Python script typically named `asgi.py` where `configure()` is called to prepare the `app` before it is served by the ASGI server.

For example, remove the call `configure()` in `app.py`:

```python
# myproject/app.py
from bocadillo import App

app = App()

# ...
```

and move it to a new `asgi.py` script:

```python
# myproject/asgi.py
from bocadillo import configure
from .app import app
from . import settings

configure(app, settings)
```

You must now serve the app using `$ uvicorn myproject.asgi:app` instead of `$ uvicorn myproject.app:app`.
