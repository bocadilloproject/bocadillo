# Recipes

Recipes (pun intended!) are objects that can be used to **group together a set of related routes**. They can later be applied to the main `API` object in order to extend its functionality in a flexible fashion.

Recipes are particularly useful when building larger, more complex applications because they allow code to be split into smaller, more manageable components.

Recipes expose the same functionality as the `API` object: you can use templates, middleware, redirects, static files, hooks, routes as you would on the regular `API` object.

## Write a recipe

The following shows an example of a very simple recipe which registers a view on the `/{ingredient}` endpoint.

```python
# tacos.py
from bocadillo import Recipe

tacos = Recipe('tacos')

@tacos.route('/{ingredient}')
def retrieve_taco(req, res, ingredient: str):
    res.media = {'ingredient': ingredient}
```

## Apply a recipe

Once you have a recipe, you can apply it to the `API` object.

```python
from tacos import tacos
import bocadillo

api = bocadillo.API()
api.recipe(tacos)

if __name__ == '__main__':
    api.run()
```

This will add all the routes in the `tacos` recipe under the `/tacos` path, meaning your app is now equipped with the `retrieve_taco` view at `/tacos/{ingredient}`. Yummy!

## Recipe books

Sometimes, you may want to group many recipes together so they can be apply all at once to the `API` object. To achieve this, you can write a **recipe book**.

Consider this example project structure, where functionality related to "entities" (people or companies) is grouped together:

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

The recipe book could be assembled as follows:

```python
# entities/people/employees.py
from bocadillo import Recipe

employees = Recipe('people_employees', prefix='/employees')

@employees.route('/{pk:d}')
async def get_employee(req, res, pk: int):
    res.media = {'id': pk, 'name': 'John Doe'}
```

```python
# entities/people/interns.py
from bocadillo import Recipe

interns = Recipe('people_interns', prefix='/interns')

@interns.route('/{pk:d}')
async def get_intern(req, res, pk: int):
    res.media = {'id': pk, 'name': 'Don Joe'}
```

```python
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

```python
# entities/__init__.py
from bocadillo import Recipe

from .people import people
from .companies import companies

entities = Recipe.book(people, companies, prefix='/entities')
```

Applying the `entities` book is straight-forward:

```python
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

## Named routes and `url_for`

If a recipe defines a named route, you'll need to prefix its name with the name of the recipe when building the full URL using `api.url_for()`.

For example:

```python
from bocadillo import Recipe

tacos = Recipe('tacos')

@tacos.route('/')
async def root(req, res):
    tacos.redirect('tacos.taco-detail', pk=4)

@tacos.route('/{pk}', name='taco-detail')
async def retrieve_taco(req, res, pk):
    res.media = {'id': pk, 'recipe': 'tacos'}
```
