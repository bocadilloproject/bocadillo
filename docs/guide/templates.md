# Templates

Bocadillo has built-in helpers for working with [Jinja2] templates. They give you all the niceties of the Jinja2 template engine: a familiar templating language, automatic escaping, template inheritance, etc.

[jinja2]: http://jinja.pocoo.org

## How templates work

To begin with, templates (when loaded from the file system) are just regular files. For example, when writing HTML templates, the regular `.html` extension is used as for any other HTML file.

::: tip
Note that a template does not _have_ to be an HTML file. Any text file will do: `.txt`, `.md`, `.rst`, etc.
:::

The only difference with regular text-based formats is that templates use a **templating language** with a set of specific tags and keywords that allow to perform **programmatic manipulations**. These are performed on **context variables** that are passed to the template when it is rendered.

## Writing templates

Bocadillo templates are powered by Jinja2 and, as such, you can use the full power of Jinja2 to write beautiful templates.

Here's an example HTML template:

```html
<!-- index.html -->
<html>
  <head>
    <title>{{ title }}</title>
  </head>
  <body>
    <h1>{{ title }}</h1>
    <p>Templates are great, aren't they?</p>
  </body>
</html>
```

Here, you can see an **interpolation** (`title` in double brackets). Upon rendering, it is replaced by the actual value of a context variable called `title` that should be passed to the rendering function (see next section).

You may find Jinja2's [Template Designer Documentation](http://jinja.pocoo.org/docs/latest/templates/) handy as a thorough description of the Jinja2 templating language.

## Rendering templates

You can render templates using the [Templates] helper. A typical use case is to create and send HTML content in HTTP views.

[templates]: /api/templates.md#templates

1. Create an instance of `Templates`:

```python
from bocadillo import App, Templates

app = App()
templates = Templates()
```

2. Render a template using `templates.render()`. You can pass context variables as keyword arguments:

```python
@app.route("/")
async def home(req, res):
    res.html = await templates.render("index.html", title="Hello, Bocadillo!")
```

Note:

- Context variables can also be given as a dictionary:

```python
await templates.render("index.html", {"title": "Hello, Bocadillo!"})
```

- You can render a template directly from a string:

```python
templates.render_string("<h1>{{ title }}</h1>", title="Hello, Bocadillo!")
# Outputs: "<h1>Hello, Bocadillo!</h1>"
```

## How templates are discovered

By default, Bocadillo looks for templates in the `templates` folder **relative to the current working directory** (which may be different from the directory where `app.py` is located).

If you generated your project using [Bocadillo CLI](https://github.com/bocadilloproject/bocadillo-cli), this means you should place templates in the project root directory:

```
.
├── myproject
│   ├── __init__.py
│   ├── app.py
│   ├── asgi.py
│   └── settings.py
└── templates
    └── index.html
```

## Changing the templates location

You can change the templates directory using the `directory` argument to `Templates`. It supports paths given as strings and [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#module-pathlib) objects.

For example, to load templates in the `templates` directory relative to where the `app.py` file is, edit `app.py` with the following:

```python
# project/app.py
from pathlib import Path
from bocadillo import App, Templates

app = App()
templates = Templates(directory=Path(__file__).parent / "templates")
```
