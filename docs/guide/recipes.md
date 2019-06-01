# Recipes

<Badge type="warn" text="Deprecated"/>

::: warning DEPRECATION NOTICE
Recipes were **deprecated** in 0.160, and will be **removed** in 0.17.0.

Please consider using [routers](/guide/routers.md) instead.
:::

**Recipes** allow to **group together a set of related routes** which can later be added to the router of the main `App` object.

Recipes are particularly useful when building larger, more complex applications because they allow code to be split into smaller, more manageable components.

## Writing recipes

The following shows an example of a very simple recipe which registers a view at the `/{ingredient}` endpoint.

```python
# myproject/recipes/tacos.py
from bocadillo import Recipe

tacos = Recipe("tacos")

@tacos.route("/{ingredient}")
async def retrieve_taco(req, res, ingredient: str):
    res.json = {"ingredient": ingredient}
```

The recipe is given the name `'tacos'`. This name is used to infer the path prefix for the recipe, i.e. `/tacos`. You can also pass a path `prefix` explicitly (which must start with `/`):

```python
tacos = Recipe("tacos", prefix="/tacos")
```

## Applying recipes

Once you have a recipe, you can apply it to an `App` instance:

```python
# myproject/app.py
from bocadillo import App
from .recipes.tacos import tacos

app = App()
app.recipe(tacos)
```

This will add all the routes in the `tacos` recipe under the `/tacos` path, meaning your app is now equipped with the `retrieve_taco` view at `/tacos/{ingredient}`. Yummy!

## Which features are available on recipes?

Since `Recipe` is a subclass of `App`, you can use all the features that are normally available to regular applications.

This includes, but is not limited to:

- [Routing](/guide/routing.md), e.g. `@recipe.route(...)` and `@recipe.websocket_route(...)`.
- [Error handling](/guide/errors.md), e.g. `@recipe.error_handler()`.
- [Middleware](/guide/middleware.md), e.g. `recipe.add_middleware(...)`.

Note, however, that:

- [Lifespan event handlers](/guide/apps.md#lifespan-events) only get called on the root application.
- Recipes cannot be nested.

#### Caveat: root routes on recipes

The fact that a `Recipe` behaves just like any other `App` also means that it applies the exact same [routing algorithm](/guide/routing.md#how-are-requests-processed) than the `App`.

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
    res.json = {'id': pk, 'name': 'John Doe'}
```

```python
# entities/people/interns.py
from bocadillo import Recipe

interns = Recipe('interns')

@interns.route('/{pk}')
async def get_intern(req, res, pk: int):
    res.json = {'id': pk, 'name': 'Don Joe'}
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
    res.json = ['Python Software Foundation']
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
