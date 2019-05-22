# Applications

A Bocadillo application is an instance of [`App`][app]. It implements the [ASGI] interface and can be served by ASGI web servers.

[app]: /api/applications.md#app
[asgi]: https://asgi.readthedocs.io

## Minimal working application

The following `app.py` script defines a **minimal working application**:

```python
from bocadillo import App, configure

app = App()
configure(app)
```

1. First, we **import** the `App` class and the `configure` helper from the `bocadillo` package.
2. Then, we **instanciate** an application.
3. Finally, the application is **configured** so that it can be served by an ASGI web server.

<!-- TODO: `bocadillo create:minimal` in a tip -->

Although this script could be served as-is, we recommend you adopt a **package-style project structure**.

To do so, place the `app.py` script in a folder containing an `__init__.py` file:

```
.
└── myproject
    ├── __init__.py
    └── app.py
```

We'll assume that you use a package-style project structure in the rest of the documentation.

## Serving an application

### Basics

The officially recommended ASGI web server for Bocadillo is [uvicorn]. It comes installed with the `bocadillo` package, so you can use it right away!

[uvicorn]: https://www.uvicorn.org

The minimal working app above can be served using:

```bash
uvicorn myproject.app:app
```

## Configuring uvicorn

You can use any of the [uvicorn settings](https://www.uvicorn.org/settings/) to configure the server.

For example, you can tell uvicorn to use port 5000 using:

```bash
uvicorn myproject.app:app --port 5000
```

## Hot reload

Hot reload is baked into uvicorn! 🚀 Use the uvicorn `--reload` argument and uvicorn will watch your files and automatically reload the whole application on each file change! This is extremely useful in a development setting.

```bash
uvicorn myproject.app:app --reload
```

## Lifespan events

Bocadillo applications implement the [ASGI Lifespan protocol](https://asgi.readthedocs.io/en/latest/specs/lifespan.html), which allows you to hook into the application's lifecycle via **event handlers**.

This is especially useful to setup resources on startup and make sure they get cleaned up when the server stops.

An event handler is an asynchronous function with the signature `() -> None`.

Event handlers can be registered using the `@app.on()` decorator:

```python
@app.on("startup")
async def setup():
    # Perform setup when server boots
    pass

@app.on("shutdown")
async def cleanup():
    # Perform cleanup when server shuts down
    pass
```

A non-decorator syntax is also available:

```python
from somelib import setup_stuff

app.on("startup", setup_stuff)
```
