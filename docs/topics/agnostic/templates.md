# Templates

Bocadillo allows you to render [Jinja2] templates.
You get all the niceties of the Jinja2 template engine:
a familiar templating language, automatic escaping, template inheritance, etc.

## How templates work

To begin with, templates are HTML files. You use the `.html` extension as for any other HTML file.

The only difference with regular HTML files is that templates provide a **templating language** with a set of specific tags and keywords that allow to perform **programmatic manipulations**. These are performed on **context variables** that are passed to the template when it is rendered.

## Writing templates

Bocadillo templates are powered by Jinja2 and, as such, you can use the full power of Jinja2 to write beautiful templates.

Here's an example template:

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

Bocadillo provides a few shortcuts to render templates. You can typically use these in views to create and return HTML content.

- Render a template using `await api.template()`. You can pass context variables as keyword arguments:

```python
async def post_detail(req, res):
    res.html = await api.template('index.html', title='Hello, Bocadillo!')
```

- In synchronous views, use `api.template_sync()` instead:

```python
def post_detail(req, res):
    res.html = api.template_sync('index.html', title='Hello, Bocadillo!')
```

- Context variables can also be given as a dictionary:

```python
await api.template('index.html', {'title': 'Hello, Bocadillo!'})
```

- Lastly, you can render a template directly from a string:

```python
>>> api.template_string('<h1>{{ title }}</h1>', title='Hello, Bocadillo!')
'<h1>Hello, Bocadillo!</h1>'
```

## How templates are discovered

By default, Bocadillo looks for templates in the `templates/` folder relative
to where the application is run. For example:

```
.
├── api.py
└── templates
    └── index.html
```

Here, using `api.template('index.html')` would load and use the template defined in the `./templates/index.html` file.

## Changing the templates location

You can change the templates directory using the `templates_dir` option to `API()`:

```python
api = bocadillo.API(templates_dir='path/to/templates')
```

[Jinja2]: http://jinja.pocoo.org
[Template Designer Documentation]: http://jinja.pocoo.org/docs/latest/templates/
