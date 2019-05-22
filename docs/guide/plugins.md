# Plugins <Badge type="warn" text="Experimental"/> <Badge text="0.14+"/>

**Plugins** allow make small pieces of functionality **configurable** and **reusable** across applications.

They solve two main use cases:

- **Improving project structure**: they can help declutter the `app.py` script in case of complex configuration-based application initialisation.
- **Sharing reusable features**: bundle a plugin into a library or a package that you or other people can reuse in various projects.

## Plugins by example

Suppose we want to allow applications to perform a configurable action when the server starts up. Here the app will print a message to the console, but the action could be anything else.

Here's what a plugin for this feature would look like:

```python
from bocadillo import plugin

@plugin
def use_startup_message(app):
    startup_message = settings.get("STARTUP_MESSAGE", "App is ready!")

    @app.on("startup")
    async def on_startup():
        print(startup_message)
```

1. We import and use the `@plugin` decorator. By doing this, the plugin is **registered** and will be called during `configure()`.
2. We define a **plugin function**, i.e. a function that takes an `app` and is conventionally named `use_X`, where `X` describes the feature that the plugin implements.
3. Inside the plugin function, we access the `STARTUP_MESSAGE` setting, and use a default value in case this setting was not defined. We then register a lifespan event handler that simply prints the message on app startup.

## Built-in plugins

Every Bocadillo application comes with a pre-defined set of plugins which enable for CORS, templates, etc.). Built-in plugins are listed in the [`plugins.py`](/api/plugins.md) API reference.

## Plugin discovery

To be executed, plugins need to be **discovered** by Bocadillo. Currently, the only way to do this is to have the Python module imported somewhere in your project, e.g. in `settings.py`:

```python
# settings.py
from someone_else_lib.plugins import *
```

::: tip NOTE
We are working on improving the plugin discovery API. See also [#284](https://github.com/bocadilloproject/bocadillo/issues/284).
:::
