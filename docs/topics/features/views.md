# Views

In Bocadillo, views are functions that take at least a request and a response
as arguments, and mutate those objects as necessary.

Views can be asynchronous or synchronous, function-based or class-based.

## Asynchronous views

The recommended way to define views in Bocadillo is using the async/await syntax. This allows you to call arbitrary asynchronous Python code:

```python
from asyncio import sleep
from bocadillo import view

async def find_post_content(slug: str):
    await sleep(1)  # perhaps query a database here?
    return 'My awesome post'

@view()
async def retrieve_post(req, res, slug: str):
    res.text = await find_post_content(slug)
```

::: tip

> Is `view()` necessary here?

TL;DR: **no**.

The role of the `view()` decorator is to build a class-based view out of a function-based view. This is because internally, Bocadillo only deals with class-based views.

Lucky you! We hide this implementation detail from you by automatically decorating function-based views when registering them via `@api.route()`.
:::

## Synchronous views

While Bocadillo is asynchronous at its core, you can also use plain Python functions to define synchronous views:

```python
@view()
def index(req, res):
    res.html = '<h1>My website</h1>'
```

**Note**: it is generally more
efficient to use asynchronous views rather than synchronous ones.
This is because, when given a synchronous view, Bocadillo needs to perform
a sync-to-async conversion, which might add extra overhead.

## Class-based views

The previous examples were function-based views, but Bocadillo also supports
class-based views.

Class-based views are regular Python classes (there is no base `View` class).
Each HTTP method gets mapped to the corresponding method on the
class. For example, `GET` gets mapped to `.get()`,
`POST` gets mapped to `.post()`, etc.

Other than that, class-based view methods are just regular views:

```python
class Index:

    async def get(self, req, res):
        res.text = 'Classes, oh my!'
       
    def post(self, req, res):
        res.text = 'Roger that'
```

A catch-all `.handle()` method can also be implemented to process all incoming
requests — resulting in other methods being ignored.

```python
class Index:

    async def handle(self, req, res):
        res.text = 'Post it, get it, put it, delete it.'
```
