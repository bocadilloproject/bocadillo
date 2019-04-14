# Recipes

```python
from bocadillo import Recipe
```

**Recipes** are objects that can be used to **group together a set of related routes**. They can later be applied to the main `App` object in order to extend its functionality in a flexible fashion.

Recipes are particularly useful when building larger, more complex applications because they allow code to be split into smaller, more manageable components.

This feature was inspired by Flask's blueprints.

## Write a recipe

The following shows an example of a very simple recipe which registers a view at the `/{ingredient}` endpoint.

```python{4}
# tacos.py
from bocadillo import Recipe

tacos = Recipe('tacos')

@tacos.route('/{ingredient}')
async def retrieve_taco(req, res, ingredient: str):
    res.media = {'ingredient': ingredient}
```

The recipe is given the name `'tacos'`. This name is used to infer the path prefix for the recipe, i.e. `/tacos`. You can also pass a path `prefix` explicitly (which must start with `/`):

```python
tacos = Recipe('tacos', prefix='/tacos')
```

## Apply a recipe

Once you have a recipe, you can apply it to the `App` object.

```python{5}
from bocadillo import App
from tacos import tacos

app = App()
app.recipe(tacos)
```

This will add all the routes in the `tacos` recipe under the `/tacos` path, meaning your app is now equipped with the `retrieve_taco` view at `/tacos/{ingredient}`. Yummy!

## Which features are available on recipes?

**You can use all the features that are normally available to a regular `App`.** In fact, the `Recipe` class is a subclass of `App`.

This includes, but is not limited to:

- [Routing](../http/routing.md), e.g. `@recipe.route(...)`, `@recipe.websocket_route(...)`, `.url_for()`, etc.
- [Error handling](../http/error-handling.md), e.g. `@recipe.error_handler()`.
- [Redirecting](../http/redirecting.md), e.g. `recipe.redirect(...)`
- [Middleware](../http/middleware.md), e.g. `recipe.add_middleware(...)`.

Note, however, that:

- [Lifespan event handlers](./events.md) only get called on the root application.
- Recipes cannot be nested.

**Caveat: root routes on recipes**

The fact that a `Recipe` behaves just like any other `App` also means that it applies the exact same [routing algorithm](../http/routing.md#how-are-requests-processed) than the `App`.

In particular, a root route `/` registered on a recipe will be mounted on the `App` at `/{recipe.prefix}/` — note the trailing slash!

```python
# app.py
from bocadillo import App, Recipe

tacos = Recipe("tacos")

@tacos.route("/")
async def index(req, res):
    res.text = "Hello, tacos!"

app = App()
app.recipe(tacos)
```

```bash
uvicorn app:app
```

```bash
$ curl http://localhost:8000/tacos
"404 Not Found"

$ curl http://localhost:8000/tacos/
"Hello, tacos!"
```

## Recipe books

Sometimes, you may want to group many recipes together so they can be applied all at once to the `App` object. To achieve this, you can write a **recipe book**.

Consider this example project structure, where functionality related people and companies has been grouped together in an `entities` package:

```
.
├── app.py
└── entities
    ├── __init__.py
    ├── companies.py
    └── people
        ├── __init__.py
        ├── employees.py
        └── interns.py
```

The `entities` recipe book could be assembled as follows:

```python
# entities/people/employees.py
from bocadillo import Recipe

employees = Recipe('employees')

@employees.route('/{pk}')
async def get_employee(req, res, pk: int):
    res.media = {'id': pk, 'name': 'John Doe'}
```

```python
# entities/people/interns.py
from bocadillo import Recipe

interns = Recipe('interns')

@interns.route('/{pk}')
async def get_intern(req, res, pk: int):
    res.media = {'id': pk, 'name': 'Don Joe'}
```

```python{7}
# entities/people/__init__.py
from bocadillo import Recipe

from .employees import employees
from .interns import interns

people = Recipe.book(employees, interns, prefix='/people')
```

```python
# entities/companies.py
from bocadillo import Recipe

companies = Recipe('companies')

@companies.route('/')
async def list_companies(req, res):
    res.media = ['Python Software Foundation']
```

```python{7}
# entities/__init__.py
from bocadillo import Recipe

from .people import people
from .companies import companies

entities = Recipe.book(people, companies, prefix='/entities')
```

Applying the `entities` book is straight-forward:

```python{5}
# app.py
from bocadillo import App
from .entities import entities

app = App()
app.recipe(entities)
```

You'll end up with the following routes:

- `/entities/people/interns/{pk}`
- `/entities/people/employees/{pk}`
- `/entities/companies/`

::: warning
Recipe books do not expose any specific features. They only serve as a means of grouping recipes together.
:::
