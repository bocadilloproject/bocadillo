# Nested applications

Bocadillo provides a simple **mounting** mechanism which allows you to make ASGI apps available at a specific URL prefix.

This applies not only to Bocadillo applications, but to **any ASGI-compliant application**. The entire ASGI ecosystem is literally just a `.mount()` away!

## Application splitting

Nested Bocadillo applications can be used to split a project into smaller applications and then tie them all together in a single _root_ application.

For example, if our project has a mix of REST API and HTML pages, we can separate the REST API endpoints in an **isolated app**:

```python
# myproject/api.py
from bocadillo import App

api = App()

@api.route("/todos")
async def get_todos(req, res):
    res.json = [{"title": "Make me a sandwich", "done": False}]
```

and then mount it onto a root application that also exposes the HTML home page:

```python
# myproject/app.py
from bocadillo import App
from .api import api

app = App()
app.mount("/api", api)

@app.route("/")
async def home(req, res):
    res.html = "<h1>Todo list</h1>"
```

With this setup, a request to `GET /api/todos` will return the list of todos.

::: warning CAVEAT
**Mounted applications are isolated from their parent**: they do not share middleware or error handlers. Besides, lifespan event handlers will only be called on the **root** application, i.e. the one that is eventually by the ASGI web server.

If you only want to split **routes** into dedicated files, take a look at [Routers](/guide/routers.md) in the next section.
:::

## Third-party ASGI apps

In fact, any application that exposes the ASGI interface can be passed to `.mount()`. This is the beauty of ASGI: its standard interface enables interoperability between otherwise incompatible applications.

As a result, **any library that provides an ASGI adapter can be used with Bocadillo**.

Here are just a few examples:

- [python-socketio](https://python-socketio.readthedocs.io/en/latest/) for high-level WebSocket programming. See also the [how-to guide](/how-to/socketio.md).
- [tartiflette-starlette](https://github.com/tartiflette/tartiflette-starlette), an ASGI adapter for the [Tartiflette](https://tartiflette.io/) async GraphQL engine.
