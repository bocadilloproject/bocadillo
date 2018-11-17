# Redirecting

Inside a view, you can redirect to another page using `api.redirect()`, which can be used in a few ways.

## By route name

Use the `name` argument:

```python
@api.route('/home', name='home')
async def home(req, res):
    res.text = f'This is home!'

@api.route('/')
async def index(req, res):
    api.redirect(name='home')
```

**Note**: route parameters can be passed as additional keyword arguments.

## By URL

You can redirect by URL by passing `url`. The URL can be internal (path relative to the server's host) or external (absolute URL).

```python
@api.route('/')
async def index(req, res):
    # internal:
    api.redirect(url='/home')
    # external:
    api.redirect(url='http://localhost:8000/home')
```

## Permanent redirections

Redirections are temporary (302) by default. To return a permanent (301) redirection, pass `permanent = True`:

```python
api.redirect(url='/home', permanent=True)
```
