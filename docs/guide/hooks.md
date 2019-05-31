# Hooks

Hooks allow you to call arbitrary code before and after a view is executed. They materialize as the [`@before()`](/api/hooks.md#before) and [`@after()`](/api/hooks.md#after) decorators located in the `bocadillo.hooks` module.

These decorators operate on a **hook function**, which is an asynchronous function with the following signature: `(req: Request, res: Response, params: dict) -> None`.

## Example

```python
from asyncio import sleep
from bocadillo import HTTPError, hooks

async def validate_has_my_header(req, res, params):
    if "x-my-header" not in req.headers:
        raise HTTPError(400)

async def show_response_content(req, res, params):
    print(res.content)

@app.route("/message")
@hooks.before(validate_has_my_header)
@hooks.after(show_response_content)
async def get_message(req, res):
    res.json = {"message": "hello"}
```

::: tip NOTE
The ordering of decorators is important: **hooks should always be a view's first decorators**.
:::

## Hooks and reusability

As a first level of reusability, you can pass extra positional or keyword arguments to `@before()` and `@after()`, and they will be handed over to the hook function:

```python
async def validate_has_header(req, res, params, header):
    if header not in req.headers:
        raise HTTPError(400)

@app.route("/message")
@hooks.before(validate_has_header, header="x-my-header")
async def get_message(req, res):
    pass
```

A hook just needs to be an asynchronous callable, so it can also be a class that implements `__call__()`. This is another convenient way of building reusable hooks functions:

```python
class RequestHasHeader:
    def __init__(self, header: str):
        self.header = header

    async def __call__(self, req, res, params):
        if self.header not in req.headers:
            raise HTTPError(400)

@app.route("/message")
@hooks.before(RequestHasHeader("x-my-header"))
async def get_message(req, res):
    pass
```

You can also use hooks on class-based views:

```python
async def show_content_type(req, res, params):
    print(res.headers["content-type"])

@app.route('/')
# applied on all method views
@hooks.after(show_content_type)
class Message:

    @hooks.before(RequestHasHeader("x-my-header"))
    async def get(self, req, res):
        res.json = {"header": req.headers["x-my-header"]}
```
