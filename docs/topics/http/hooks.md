# Hooks

## What are hooks?

Hooks allow you to call arbitrary code before and after a view is executed. They materialize as the `@api.before()` and `@api.after()` decorators.
 
These decorators take a **hook function**, which is a synchronous or asynchronous function with the following signature: `(req: Request, res: Response, params: dict) -> None`.

## Example

```python
from asyncio import sleep
from bocadillo import HTTPError

def validate_has_my_header(req, res, params):
    if 'x-my-header' not in req.headers:
        raise HTTPError(400)

async def validate_response_is_json(req, res, params):
    await sleep(1)  # for the sake of example
    assert res.headers['content-type'] == 'application/json'

@api.before(validate_has_my_header)
@api.after(validate_response_is_json)
@api.route('/foo')
async def foo(req, res):
    res.media = {'message': 'valid!'}
```

::: warning
Due to the way hooks are implemented, you must always put `@api.before()` and `@api.after()` **above** the `@api.route()` decorator.
:::

## Hooks and reusability

As a first level of reusability, you can pass extra positional or keyword arguments to `@api.before()` and `@api.after()`, and they will be handed over to the hook function:

```python
def validate_has_header(req, res, params, header):
    if header not in req.headers:
        raise HTTPError(400)

@api.before(validate_has_header, 'x-my-header')
@api.route('/foo')
async def foo(req, res):
    pass
```

A hook function only just needs to be a callable, so it can be a class that implements `__call__()` too. This is another convenient way of building reusable hooks functions:

```python
class RequestHasHeader:
    
    def __init__(self, header):
        self.header = header
       
    def __call__(self, req, res, params):
        if self.header not in req.headers:
            raise HTTPError(400)

@api.before(RequestHasHeader('x-my-header'))
@api.route('/foo')
async def foo(req, res):
    pass
```

You can also use hooks on class-based views:

```python
def show_content_type(req, res, view, params):
    print(res.headers['content-type'])

@api.after(show_content_type)
@api.route('/')
class Foo:

    @api.before(RequestHasHeader('x-my-header'))
    async def get(self, req, res):
        res.media = {'header': req.headers['x-my-header']}
```
