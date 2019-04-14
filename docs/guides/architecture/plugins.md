# Plugins

::: warning
This is an advanced topic. You typically won't need to know about this when getting started with the framework.
:::

Bocadillo provides a simple plugin architecture to hook into [application configuration](/guides/architecture/app.md#configuration) and extend the behavior of an application.

## How plugins work

When `configure()` is called, settings are populated and plugins are called and given the `app` being configured as argument.

A plugin is a callable that should take an `App` instance as its unique parameter. A plugin can perform any operation required to achieve the desired behavior: register routes, setup event handlers, register middleware, etc.

## Registering plugins

Plugins can be registered using the `@plugin` decorator. Once registered, a plugin will be called when configuring an application. See [Writing plugins](#writing-plugins) for example usage.

## Built-in plugins

The [plugins module](/api/plugins.md) lists built-in plugins and the settings they use. They implement features such as CORS, GZip compression, static files, and more.

## Inspecting plugins

Plugins are stored at the global level. You can retrieve them using the `get_plugins()` helper:

```python
from bocadillo import get_plugins

print(get_plugins())
```

## Writing plugins

To create your own plugin, define a **plugin function** with the signature `(app: App) -> None`. By convention, this function should be named `use_xyz` where `xyz` describes the feature this plugin implements (e.g. `use_cors`, `use_static`, etc.).

For example, here's a plugin function that prints a message on application startup:

```python
from bocadillo import plugin

@plugin
def use_startup_hello(app):
    @app.on("startup")
    async def hello():
        print("Hello, app!")
```

Plugins can use the `settings` helper (see [Retrieving settings](/guides/architecture/app.md#retrieving-settings)) to change their behavior based on app configuration:

```python
from bocadillo import plugin, settings

@plugin
def use_startup_message(app):
    message = settings.get("STARTUP_MESSAGE", "Hello, app!")

    @app.on("startup")
    async def hello():
        print(message)
```
