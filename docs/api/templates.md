# bocadillo.templates

## TemplatesMixin
```python
TemplatesMixin(self, templates_dir: str = None, **kwargs)
```
Provide templating capabilities to an application class.
### templates_dir
The path where templates are searched for, or `None` if not set.

This is built from the `templates_dir` parameter.

### template
```python
TemplatesMixin.template(self, name_: str, context: dict = None, **kwargs) -> Coroutine
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
TemplatesMixin.template_sync(self, name_: str, context: dict = None, **kwargs) -> str
```
Render a template synchronously.

See also: `API.template()`.

### template_string
```python
TemplatesMixin.template_string(self, source: str, context: dict = None, **kwargs) -> str
```
Render a template from a string (synchronous).

__Parameters__

- __source (str)__: a template given as a string.

For other parameters, see `API.template()`.

