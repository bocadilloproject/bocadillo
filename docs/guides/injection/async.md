# Asynchronous providers

Up to now, we've only built _synchronous_ providers, i.e. ones whose provider function is declared with `def`.

Of course, Bocadillo also supports **asynchronous providers**. Those are declared with `async def` and are evaluated (`await`ed) before being injected into the view.

## Example: fetching JSON data

Here's an example async provider that draws random JSON data from [HTTPBin](https://httpbin.org) using [aiohttp](https://aiohttp.readthedocs.io):

```python
import aiohttp
from bocadillo import App, provider

@provider
async def some_json():
    async with aiohttp.ClientSession() as session:
        async with session("https://httpbin.org/json") as response:
            return await response.json()

app = App()

@app.route("/data")
async def data(req, res, some_json: dict):
    res.media = random_json  # NOTE: no need to `await`
```

::: tip
When given the `app` [scope](#scopes), an async provider is only awaited once — the first time it is used. Its result is then cached and reused.

While this is the normal behavior for app-scoped providers, this makes reusing an async provider very cheap because calls to the network/filesystem/etc are only made once.
:::

## Lazy evaluation

If you need to defer evaluating an async provider until you really need it, you can declare it as `lazy`:

```python
import aiohttp
from bocadillo import App, provider

@provider(lazy=True)
async def random_json():
    async with aiohttp.ClientSession() as session:
        async with session("https://httpbin.org/json") as resp:
            return await resp.json()

app = App()

@app.route("/data")
async def data(req, res, random_json: Awaitable[dict]):
    if req.query_params.get("random"):
        res.media = await random_json
    else:
        res.media = {"value": 42}
```

::: warning CAVEAT
Lazy providers can only be **request-scoped**. If it could be app-scoped, Bocadillo would have no way to know whether it has already been awaited when handling another connection.
:::
