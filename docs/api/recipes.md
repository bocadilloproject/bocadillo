# bocadillo.recipes

## RecipeBase
```python
RecipeBase(self, prefix: str)
```
Definition of the recipe interface.
## Recipe
```python
Recipe(self, name: str, prefix: str = None, **kwargs)
```
A grouping of capabilities that can be merged back into an API.

__Parameters__


- __name (str)__:
    A name for the recipe.
- __prefix (str)__:
    The path prefix where the recipe will be mounted.
    Defaults to `"/" + name`.
- __templates_dir (str)__:
    See `API`.

### templates_dir
The path where templates are searched for, or `None` if not set.

This is built from the `templates_dir` parameter.

### route
```python
Recipe.route(self, pattern: str, **kwargs)
```
Register a route on the recipe.

Accepts the same arguments as `API.route()`, except `namespace` which
will be given the value of the recipe's `name`.

__See Also__

- [API.route()](./api.md#route)

### websocket_route
```python
Recipe.websocket_route(self, pattern: str, **kwargs)
```
Register a WebSocket route on the recipe.

Accepts the same arguments as `API.websocket_route()`.

__See Also__

- [API.websocket_route()](./api.md#websocket-route)

### template
```python
Recipe.template(self, name_: str, context: dict = None, **kwargs) -> Coroutine
```
Render a template asynchronously.

Can only be used within `async` functions.

__Parameters__


- __name (str)__:
    Name of the template, located inside `templates_dir`.
    The trailing underscore avoids collisions with a potential
    context variable named `name`.
- __context (dict)__:
    Context variables to inject in the template.
- __kwargs (dict)__:
    Context variables to inject in the template.

### book
```python
Recipe.book(*recipes: 'Recipe', prefix: str) -> 'RecipeBook'
```
Build a book of recipes.

Shortcut for `RecipeBook(recipes, prefix)`.

### template_sync
```python
Recipe.template_sync(self, name_: str, context: dict = None, **kwargs) -> str
```
Render a template synchronously.

See also: `API.template()`.

### template_string
```python
Recipe.template_string(self, source: str, context: dict = None, **kwargs) -> str
```
Render a template from a string (synchronous).

__Parameters__

- __source (str)__: a template given as a string.

For other parameters, see `API.template()`.

## RecipeBook
```python
RecipeBook(self, recipes: Sequence[bocadillo.recipes.Recipe], prefix: str)
```
A composition of multiple recipes.

__Parameters__

- __recipes (list)__: a list of `Recipe` objects.
- __prefix (str)__:
    A prefix that will be prepended to all of the recipes' prefixes.

