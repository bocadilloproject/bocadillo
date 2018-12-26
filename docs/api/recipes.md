# bocadillo.recipes

## RecipeBase
```python
RecipeBase(self, /, *args, **kwargs)
```
Definition of the recipe interface.
### apply
```python
RecipeBase.apply(self, api, root: str = '')
```
Apply the recipe to an API object.

Should be implemented by subclasses.

__Parameters__

- __api (API)__: an API object.
- __root (str)__: a root URL path itself prefixed to the recipe's `prefix`.

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

### template_sync
```python
Recipe.template_sync(self, name_: str, context: dict = None, **kwargs) -> str
```
Render a template synchronously.

See also: `API.template()`.

### route
```python
Recipe.route(self, *args, **kwargs)
```
Register a route on the recipe.

Accepts the same arguments as `API.route()`, except `namespace` which
is given the value of the recipe's `name`.

__See Also__

- [API.route()](./api.md#route)

### template_string
```python
Recipe.template_string(self, source: str, context: dict = None, **kwargs) -> str
```
Render a template from a string (synchronous).

__Parameters__

- __source (str)__: a template given as a string.

For other parameters, see `API.template()`.

### before
```python
Recipe.before(self, hook_function: Callable[[bocadillo.request.Request, bocadillo.response.Response, dict], Coroutine], *args, **kwargs)
```
Register a before hook on a route.

::: tip NOTE
`@api.before()` should be placed  **above** `@api.route()`
when decorating a view.
:::

__Parameters__

- __hook_function (callable)__:            A synchronous or asynchronous function with the signature:
    `(req, res, params) -> None`.

### apply
```python
Recipe.apply(self, api, root: str = '')
```
Apply the recipe to an API object.

This will:

- Mount registered routes onto the `api`.
- Update the templates directory to that of `api`.

__See Also__

- [RecipeBase.apply()](#apply)

### after
```python
Recipe.after(self, hook_function: Callable[[bocadillo.request.Request, bocadillo.response.Response, dict], Coroutine], *args, **kwargs)
```
Register an after hook on a route.

::: tip NOTE
`@api.after()` should be placed **above** `@api.route()`
when decorating a view.
:::

__Parameters__

- __hook_function (callable)__:            A synchronous or asynchronous function with the signature:
    `(req, res, params) -> None`.

### book
```python
Recipe.book(*recipes: 'Recipe', prefix: str) -> 'RecipeBook'
```
Build a book of recipes.

Shortcut for `RecipeBook(recipes, prefix)`.

## RecipeBook
```python
RecipeBook(self, recipes: Sequence[bocadillo.recipes.Recipe], prefix: str)
```
A composition of multiple recipes.

__Parameters__

- __recipes (list)__: a list of `Recipe` objects.
- __prefix (str)__:
    A prefix that will be prepended to all of the recipes' own prefixes.

### apply
```python
RecipeBook.apply(self, api, root: str = '')
```
Apply the recipe book to an API object.

This is equivalent to calling `recipe.apply(api, root=root + self.prefix)`
for each of the book's recipes.

__See Also__

- [RecipeBase.apply()](#apply)

