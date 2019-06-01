# Routers

Real-world web applications typically consist of many routes. Putting them all in a single `app.py` file can quickly be hard to maintain.

**Routers** allow you to group related routes into dedicated files, resulting in more decoupled and maintainable code.

## Routers by example

Suppose we are building a REST API which deals with two resources: **users** and **todo items**.

Instead of placing all the routes in `app.py`, let's keep things organized and create a router for each resource. We'll then be able to register all the routes onto the main application.

For example, let's start with the users router:

```python
# myproject/routers/users.py
from bocadillo import Router

router = Router()

@router.route("/users")
async def list_users(req, res):
    ...

@router.route("/users/{pk}")
async def retrieve_user(req, res, pk: int):
    ...
```

We can use `app.include_router()` to add all the routes from this router in `app.py`:

```python{3,6}
# myproject/app.py
from bocadillo import App
from .routers import users

app = App()
app.include_router(users.router)
```

Here's the todos router:

```python
# myproject/routers/todos.py
from bocadillo import Router

router = Router()

@router.route("/")
async def list_todos(req, res):
    ...

@router.route("/{pk}")
async def retrieve_todo(req, res, pk: int):
    ...
```

Routers also support WebSocket routes, so let's add one for the sake of example:

```python
@router.websocket_route("/shared")
async def synchronize_shared_todos(ws):
    ...
```

Notice how we didn't repeat `/todos` in the URL pattern here? We can actually define it just once by passing a `prefix` to `app.include_router()`:

```python{3,7}
# myproject/app.py
from bocadillo import App
from .routers import users, todos

app = App()
app.include_router(users.router)
app.include_router(todos.router, prefix="/todos")
```

To wrap this up, here is the final file structure:

```
.
└── myproject
    ├── __init__.py
    ├── app.py
    ├── asgi.py
    ├── routers
    │   ├── __init__.py
    │   ├── todos.py
    │   └── users.py
    └── settings.py
```
