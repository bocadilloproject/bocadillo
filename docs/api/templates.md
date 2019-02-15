# bocadillo.templates

## Templates
```python
Templates(self, app: Union[Any, NoneType] = None, directory: str = 'templates', context: dict = None)
```
This class provides templating capabilities.

This is a light wrapper around [jinja2](http://jinja.pocoo.org/docs) and using it requires to install Bocadillo using the `[templates]` extra.

See also [Templates](../guides/agnostic/templates.md) for detail.

[RoutingMixin]: ./routing.md#routingmixin

__Parameters__


::: tip
These parameters are also stored as attributes and can be accessed or
modified at runtime.
:::

- __app (any)__:
    an optional application object. May be a subclass of [RoutingMixin].
- __directory (str)__:
    The directory where templates should be searched for.
    Passed to the `engine`.
    Defaults to `"templates"` relative to the current working directory.
- __context (dict, optional)__:
    Global template variables passed to the `engine`.
    If present, the app's `.url_for()` method is registered as
    an `url_for` global variable.

### render
```python
Templates.render(self, filename: str, *args: dict, **kwargs: str) -> str
```
Render a template asynchronously.

Can only be used within async functions.

__Parameters__

- __name (str)__:
    Name of the template, located inside `templates_dir`.
    The trailing underscore avoids collisions with a potential
    context variable named `name`.
- __*args (dict)__:
    Context variables to inject in the template.
- __*kwargs (str)__:
    Context variables to inject in the template.

### render_sync
```python
Templates.render_sync(self, filename: str, *args: dict, **kwargs: str) -> str
```
Render a template synchronously.

__See Also__

[Templates.render](#render) for the accepted arguments.

### render_string
```python
Templates.render_string(self, source: str, *args: dict, **kwargs: str) -> str
```
Render a template from a string (synchronously).

__Parameters__

- __source (str)__: a template given as a string.

__See Also__

[Templates.render](#render) for the other accepted arguments.

