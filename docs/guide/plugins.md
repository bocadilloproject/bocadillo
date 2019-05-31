# Plugins

<Badge type="warn" text="Experimental"/><Badge text="0.14+"/>

**Plugins** allow to make small pieces of functionality **configurable** and **reusable** across applications and projects.

They solve two main use cases:

- **Improving project structure**: they can help declutter the `app.py` script in case of complex configuration-based application initialisation.
- **Sharing reusable features**: bundle a plugin into a library or a package which other people can reuse.

## Writing your own plugins

Suppose we want to allow applications to perform a configurable action when the server starts up. As a contrived example, we will print a message to the console, but the action can be anything else.

Here's what a plugin for this feature would look like:

```python
def use_startup_message(app):
    message = settings.get("STARTUP_MESSAGE")
    if message is None:
        return

    @app.on("startup")
    async def on_startup():
        print(message)
```

1. We define a **plugin function** which accepts the `app` as input. By convention, it should be named `use_X`, where `X` describes the feature that the plugin implements.
2. Inside the plugin function, we access the `STARTUP_MESSAGE` setting and, if it is defined, we register a lifespan event handler on the app.

## Where should plugins be located?

If you intend to use it for your own project, consider putting it in a `plugins` module, e.g. `myproject/plugins.py`.

If you're bundling the plugin into a package, you should also place it in a `plugins` module, e.g. `my_third_party_lib/plugins.py`.

## Using plugins

Once registered, a plugin is executed during the [configuration](/guide/config.md) phase, i.e. when calling `configure()`.

To register plugins, use the `PLUGINS` setting:

```python
# myproject/settings.py
from starlette.config iport Config
from third_party_logs.plugins import use_startup_message

config = Config(".env")

PLUGINS = [
    use_startup_message,
]

STARTUP_MESSAGE = config("STARTUP_MESSAGE", default="App is ready!")
```

## Conditional plugin registration

Instead of plugin functions, items in the list of `PLUGINS` can be dictionaries that map plugins to boolean values indicating whether they should be registered or ignored.

This is a very powerful feature — for example, you can enable/disable features (or even entire sections of the app) based on environment variables:

```python
# myproject/plugins.py
def use_auth_routes(app):
    @app.route("/login")
    async def login(req, res):
        ...  # TODO

    @app.route("/logout")
    async def logout(req, res):
        ...  # TODO
```

```python
# myproject/settings.py
from starlette.config import Config
from third_party_logs.plugins import use_startup_message
from myproject.plugins import use_auth_routes

config = Config(".env")

PLUGINS = [
    {
        use_startup_message: config("VERBOSE"),
        use_auth_routes: config("ENABLE_AUTH", cast=bool, default=False)
    },
]

STARTUP_MESSAGE = "App is ready!"
```

## Built-in plugins

Every Bocadillo application comes with a pre-defined set of plugins which enable various features (CORS, HSTS, static files, etc.). Built-in plugins are listed in the [`plugins.py`](/api/plugins.md) API reference.

Most built-in plugins are disabled by default. For this reason, we don't currently provide a way to unregister them.
