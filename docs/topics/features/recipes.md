# Recipes

**Recipes** are objects that can be used to **group together a set of related routes**. They can later be applied to the main `API` object in order to extend its functionality in a flexible fashion.

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

Once you have a recipe, you can apply it to the `API` object.

```python{5}
import bocadillo
from tacos import tacos

api = bocadillo.API()
api.recipe(tacos)

if __name__ == '__main__':
    api.run()
```

This will add all the routes in the `tacos` recipe under the `/tacos` path, meaning your app is now equipped with the `retrieve_taco` view at `/tacos/{ingredient}`. Yummy!

## Which features are available on recipes?

Recipes expose the following features, which can be used just as you would on the `API` object:

- [Routes](../request-handling/routes-url-design.md), e.g. `@recipe.route()`.
- [Templates](./templates.md), e.g. `await recipe.template()`.

::: tip
If your recipe needs to use its own templates, you should pass an adequate `templates_dir` to the `Recipe` constructor. Otherwise, the same `templates_dir` as the `API` will be used.
:::

::: warning CAVEAT
Note that recipes apply the exact same [routing algorithm](../request-handling/routes-url-design.md#how-are-requests-processed) than the `API`. In particular, the `/` route will be mounted on the `API` at `/{prefix}/`, *not* `/prefix`. Accessing `/prefix` would return a 404 error, as per the routing algorithm.
:::

## Recipe books

Sometimes, you may want to group many recipes together so they can be apply all at once to the `API` object. To achieve this, you can write a **recipe book**.

Consider this example project structure, where functionality related people and companies has been grouped together in an `entities` package:

```
.
├── api.py
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

api = bocadillo.API()
api.recipe(entities)

if __name__ == '__main__':
    api.run()
```

You'll end up with the following routes:

- `/entities/people/interns/{pk}`
- `/entities/people/employees/{pk}`
- `/entities/companies/`

::: warning
Recipe books do not expose the `API` API. They only serve as a means of grouping recipes together.
:::

## Named routes and `url_for`

If a recipe defines a named route, you'll need to prefix its name with the name of the recipe when building the full URL using `api.url_for()`.

For example:

```python{7}
from bocadillo import Recipe

tacos = Recipe('tacos')

@tacos.route('/')
async def root(req, res):
    tacos.redirect('tacos.taco-detail', pk=4)

@tacos.route('/{pk}', name='taco-detail')
async def retrieve_taco(req, res, pk):
    res.media = {'id': pk, 'recipe': 'tacos'}
```
