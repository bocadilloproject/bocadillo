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

### templates_dir
The path where templates are searched for, or `None` if not set.

::: warning DEPRECATED
`templates_dir` was **deprecated** in v0.12, and will be **removed** in v0.13. Please use [`bocadillo.templates.Templates.directory`](./templates.md#Templates) instead.
:::



This is built from the `templates_dir` parameter.
### template
```python
Recipe.template(self, name_: str, *args: dict, **kwargs: Any) -> str
```
Render a template asynchronously.

::: warning DEPRECATED
`template` was **deprecated** in v0.12, and will be **removed** in v0.13. Please use [`bocadillo.templates.Templates.render`](./templates.md#render) instead.
:::



Can only be used within `async` functions.

__Parameters__

- __name (str)__:
    Name of the template, located inside `templates_dir`.
    The trailing underscore avoids collisions with a potential
    context variable named `name`.
- __*args (dict)__:
    Context variables to inject in the template.
- __**kwargs (any)__:
    Context variables to inject in the template.
### route
```python
Recipe.route(self, pattern: str, **kwargs) -> bocadillo.routing.HTTPRoute
```
Register a new route by decorating a view.

__Parameters__

- __pattern (str)__: an URL pattern.
- __methods (list of str)__:
    An optional list of HTTP methods.
    Defaults to `["get", "head"]`.
    Ignored for class-based views.
- __name (str)__:
    An optional name for the route.
    If a route already exists for this name, it is replaced.
    Defaults to a snake-cased version of the view's name.
- __namespace (str)__:
    An optional namespace for the route. If given, it is prefixed to
    the name and separated by a colon.

### websocket_route
```python
Recipe.websocket_route(self, pattern: str, **kwargs) -> bocadillo.routing.WebSocketRoute
```
Register a WebSocket route by decorating a view.

__Parameters__

- __pattern (str)__: an URL pattern.

__See Also__

- [WebSocket](./websockets.md#websocket) for a description of keyword
arguments.

### template_sync
```python
Recipe.template_sync(self, name_: str, *args: dict, **kwargs: Any) -> str
```
Render a template synchronously.

::: warning DEPRECATED
`template_sync` was **deprecated** in v0.12, and will be **removed** in v0.13. Please use [`bocadillo.templates.Templates.render_sync`](./templates.md#render-sync) instead.
:::



For parameters, see [.template()](#template).
### template_string
```python
Recipe.template_string(self, source: str, *args: dict, **kwargs: Any) -> str
```
Render a template from a string (synchronous).

::: warning DEPRECATED
`template_string` was **deprecated** in v0.12, and will be **removed** in v0.13. Please use [`bocadillo.templates.Templates.render_string`](./templates.md#render-string) instead.
:::



__Parameters__

- __source (str)__: a template given as a string.

For other parameters, see [.template()](#template).
### book
```python
Recipe.book(*recipes: 'Recipe', prefix: str) -> 'RecipeBook'
```
Build a book of recipes.

Shortcut for `RecipeBook(recipes, prefix)`.

### url_for
```python
Recipe.url_for(self, name: str, **kwargs) -> str
```
Build the full URL path for a named route.

__Parameters__

- __name (str)__: the name of the route.
- __kwargs (dict)__: route parameters.

__Returns__

`url (str)`: an URL path.

__Raises__

- `HTTPError(404) `: if no route exists for the given `name`.

### redirect
```python
Recipe.redirect(self, *, name: str = None, url: str = None, permanent: bool = False, **kwargs) -> NoReturn
```
Redirect to another HTTP route.

This is only meant to be used inside an HTTP view.

__Parameters__

- __name (str)__: name of the route to redirect to.
- __url (str)__:
    URL of the route to redirect to (required if `name` is omitted).
- __permanent (bool)__:
    If `False` (the default), returns a temporary redirection (302).
    If `True`, returns a permanent redirection (301).
- __kwargs (dict)__:
    Route parameters.

__Raises__

- `Redirection`:
    an exception that will be caught to trigger a redirection.

__See Also__

- [Redirecting](../guides/http/redirecting.md)

## RecipeBook
```python
RecipeBook(self, recipes: Sequence[bocadillo.recipes.Recipe], prefix: str)
```
A composition of multiple recipes.

__Parameters__

- __recipes (list)__: a list of `Recipe` objects.
- __prefix (str)__:
    A prefix that will be prepended to all of the recipes' prefixes.

