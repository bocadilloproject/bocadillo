# bocadillo.deprecated.templates

## TemplatesMixin
```python
TemplatesMixin(self, templates_dir: str = 'templates', **kwargs)
```
Provide templating capabilities to an application class.

::: warning DEPRECATED
`TemplatesMixin` was **deprecated** in v0.12, and will be **removed** in v0.13. Please use [`bocadillo.templates.Templates`](./templates.md#Templates) instead.
:::



### templates_dir
The path where templates are searched for, or `None` if not set.

::: warning DEPRECATED
`templates_dir` was **deprecated** in v0.12, and will be **removed** in v0.13. Please use [`bocadillo.templates.Templates.directory`](./templates.md#Templates) instead.
:::



This is built from the `templates_dir` parameter.
### template
```python
TemplatesMixin.template(self, name_: str, *args: dict, **kwargs: Any) -> str
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
### template_sync
```python
TemplatesMixin.template_sync(self, name_: str, *args: dict, **kwargs: Any) -> str
```
Render a template synchronously.

::: warning DEPRECATED
`template_sync` was **deprecated** in v0.12, and will be **removed** in v0.13. Please use [`bocadillo.templates.Templates.render_sync`](./templates.md#render-sync) instead.
:::



For parameters, see [.template()](#template).
### template_string
```python
TemplatesMixin.template_string(self, source: str, *args: dict, **kwargs: Any) -> str
```
Render a template from a string (synchronous).

::: warning DEPRECATED
`template_string` was **deprecated** in v0.12, and will be **removed** in v0.13. Please use [`bocadillo.templates.Templates.render_string`](./templates.md#render-string) instead.
:::



__Parameters__

- __source (str)__: a template given as a string.

For other parameters, see [.template()](#template).
