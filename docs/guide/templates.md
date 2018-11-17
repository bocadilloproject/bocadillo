# Templates

Bocadillo allows you to render [Jinja2](http://jinja.pocoo.org) templates.
You get all the niceties of the Jinja2 template engine:
a familiar templating language, automatic escaping, template inheritance, etc.

## Rendering templates

You can render a template using `await api.template()`:

```python
async def post_detail(req, res):
    res.html = await api.template('index.html', title='Hello, Bocadillo!')
```

In synchronous views, use `api.template_sync()` instead:

```python
def post_detail(req, res):
    res.html = api.template_sync('index.html', title='Hello, Bocadillo!')
```

Context variables can also be given as a dictionary:

```python
await api.template('index.html', {'title': 'Hello, Bocadillo!'})
```

Lastly, you can render a template directly from a string:

```python
>>> api.template_string('<h1>{{ title }}</h1>', title='Hello, Bocadillo!')
'<h1>Hello, Bocadillo!</h1>'
```

## Templates location

By default, Bocadillo looks for templates in the `templates/` folder relative
to where the app is executed. For example:

```
.
├── app.py
└── templates
    └── index.html
```

You can change the templates directory using the `templates_dir` option:

```python
api = bocadillo.API(templates_dir='path/to/templates')
```
