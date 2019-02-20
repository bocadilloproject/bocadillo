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
def retrieve_taco(req, res, ingredient: str):
    res.media = {'ingredient': ingredient}
```

The recipe is given the name `'tacos'`. This name is used to infer the path prefix for the recipe, i.e. `/tacos`. You can also pass a path `prefix` explicitly (which must start with `/`):

```python
tacos = Recipe('tacos', prefix='/tacos')
```

## Apply a recipe

Once you have a recipe, you can apply it to the `App` object.

```python{5}
import bocadillo
from tacos import tacos

app = bocadillo.App()
app.recipe(tacos)

if __name__ == '__main__':
    app.run()
```

This will add all the routes in the `tacos` recipe under the `/tacos` path, meaning your app is now equipped with the `retrieve_taco` view at `/tacos/{ingredient}`. Yummy!

## Which features are available on recipes?

Recipes expose the following features, which can be used just as you would on the `App` object:

- [HTTP routes](../http/routing.md), e.g. `@recipe.route()`.
- [WebSocket routes](../websockets/routing.md), .e.g `@recipe.websocket_route()`.
- [HTTP redirects](../http/redirecting.md), e.g. `recipe.redirect(name="recipe:foo")`.
- [Templates](./templates.md), e.g. `await recipe.template()`.

::: tip
The `url_for()` template global is also available from recipes, and works no differently than for the `App`.

This means that you must use the namespaced name if the target route has been registered on the recipe, e.g. `url_for("recipe:foo")`.

See [Reversing named routes](../http/routing.md#reversing-named-routes) for more information on `url_for()`.
:::

::: tip
If your recipe needs to use its own templates, you can pass an adequate `templates_dir` to the `Recipe` constructor. Otherwise, the same `templates_dir` as the `App` will be used.
:::

::: tip
You can decorate your recipe views with [hooks](../http/hooks.md) as usual.
:::

::: warning CAVEAT
Note that recipes apply the exact same [routing algorithm](../http/routing.md#how-are-requests-processed) than the `App`. In particular, the `/` route will be mounted on the `App` at `/{prefix}/`, _not_ `/{prefix}`. Accessing `/{prefix}` would return a 404 error, as per the routing algorithm.
:::

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

@employees.route('/{pk:d}')
async def get_employee(req, res, pk: int):
    res.media = {'id': pk, 'name': 'John Doe'}
```

```python
# entities/people/interns.py
from bocadillo import Recipe

interns = Recipe('interns')

@interns.route('/{pk:d}')
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
import bocadillo
from .entities import entities

app = bocadillo.App()
app.recipe(entities)

if __name__ == '__main__':
    app.run()
```

You'll end up with the following routes:

- `/entities/people/interns/{pk}`
- `/entities/people/employees/{pk}`
- `/entities/companies/`

::: warning
Recipe books do not expose any specific features. They only serve as a means of grouping recipes together.
:::
