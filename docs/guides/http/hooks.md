# Hooks

## What are hooks?

Hooks allow you to call arbitrary code before and after a view is executed. They materialize as the `@before()` and `@after()` decorators located in the `bocadillo.hooks` module.

These decorators take a **hook function**, which is a asynchronous function with the following signature: `(req: Request, res: Response, params: dict) -> None`.

## Example

```python
from asyncio import sleep
from bocadillo import HTTPError, hooks

async def validate_has_my_header(req, res, params):
    if 'x-my-header' not in req.headers:
        raise HTTPError(400)

async def validate_response_is_json(req, res, params):
    await sleep(1)  # for the sake of example
    assert res.headers['content-type'] == 'application/json'

@app.route('/foo')
@hooks.before(validate_has_my_header)
@hooks.after(validate_response_is_json)
async def foo(req, res):
    res.media = {'message': 'valid!'}
```

::: tip
The ordering of decorators is important: **hooks should always be a view's first decorators**.
:::

## Hooks and reusability

As a first level of reusability, you can pass extra positional or keyword arguments to `@app.before()` and `@app.after()`, and they will be handed over to the hook function:

```python
async def validate_has_header(req, res, params, header):
    if header not in req.headers:
        raise HTTPError(400)

@app.route('/foo')
@hooks.before(validate_has_header, 'x-my-header')
async def foo(req, res):
    pass
```

A hook just needs to be an asynchronous callable, so it can be a class that implements `__call__()` too. This is another convenient way of building reusable hooks functions:

```python
class RequestHasHeader:

    def __init__(self, header):
        self.header = header

    async def __call__(self, req, res, params):
        if self.header not in req.headers:
            raise HTTPError(400)

@app.route('/foo')
@hooks.before(RequestHasHeader('x-my-header'))
async def foo(req, res):
    pass
```

You can also use hooks on class-based views:

```python
async def show_content_type(req, res, view, params):
    print(res.headers['content-type'])

@app.route('/')
# applied on all method views
@hooks.after(show_content_type)
class Foo:

    @hooks.before(RequestHasHeader('x-my-header'))
    async def get(self, req, res):
        res.media = {'header': req.headers['x-my-header']}
```
