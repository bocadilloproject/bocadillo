# Templates

Bocadillo allows you to render [Jinja2] templates.
You get all the niceties of the Jinja2 template engine:
a familiar templating language, automatic escaping, template inheritance, etc.

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

You may find Jinja2's [Template Designer Documentation] handy as a thorough description of the Jinja2 templating language.

## Rendering templates

You can render templates using the [Templates] helper. A typical use case is to create and send HTML content in HTTP views.

[templates]: ../../api/templates.md#templates

1. Create an instance of `Templates`:

```python
from bocadillo import App, Templates

app = App()
templates = Templates(app)
```

2. Render a template using `templates.render()`. You can pass context variables as keyword arguments:

```python
async def post_detail(req, res):
    res.html = await templates.render("index.html", title="Hello, Bocadillo!")
```

- Context variables can also be given as a dictionary:

```python
await templates.render("index.html", {"title": "Hello, Bocadillo!"})
```

- You can render a template directly from a string:

```python
templates.render_string('<h1>{{ title }}</h1>', title='Hello, Bocadillo!')
# Outputs: "<h1>Hello, Bocadillo!</h1>"
```

## How templates are discovered

### Default location

By default, Bocadillo looks for templates in the `templates/` folder relative
to where the application is run. For example:

```
.
├── app.py
└── templates
    └── index.html
```

Here, using `await templates.render('index.html')` would load and use the template defined in the `./templates/index.html` file.

### Changing the templates location

You can change the templates directory by passing the path to a `directory` to `Templates`:

```python
templates = Templates(directory='path/to/templates')
```

## Using templates outside an application

It is not mandatory that you pass an `App` instance when creating a `Templates` helper. All it does is try to configure some global variables for you, such as `url_for()` in order to reference absolute URLs.

This means that `Templates` can be used to perform _any_ templating task.

For example, let's render email! 📨

```python
from bocadillo.templates import Templates

email = Templates(directory="email/templates")
content = email.render_sync("welcome.md", username="lazydog")
```

[jinja2]: http://jinja.pocoo.org
[template designer documentation]: http://jinja.pocoo.org/docs/latest/templates/
