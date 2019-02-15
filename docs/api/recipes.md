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

__See Also__

- [check_route](#check-route) for the route validation algorithm.

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
Build the URL path for a named route.

__Parameters__

- __name (str)__: the name of the route.
- __kwargs (dict)__: route parameters.

__Returns__

`url (str)`: the URL path for a route.

__Raises__

- `HTTPError(404) `: if no route exists for the given `name`.

### redirect
```python
Recipe.redirect(self, *, name: str = None, url: str = None, permanent: bool = False, **kwargs)
```
Redirect to another HTTP route.

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

