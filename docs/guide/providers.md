# Providers <Badge text="Experimental" type="warn"/> <Badge text="0.13+"/>

**Providers** solve the problem of injecting reusable resources into HTTP and WebSocket views in an explicit, modular and async-capable manner, without having to rely on global variables or numerous import statements.

In practice, you can view providers as a **runtime dependency injection system**.

The API for providers was heavily influenced by [pytest fixtures](https://docs.pytest.org/en/latest/provider.html), so it should feel fairly familiar. Also, their core implementation was extracted into a separate, officially supported package: [aiodine](https://github.com/bocadilloproject/aiodine).

## Example

Suppose we want to implement a cache system backed by [Redis](https://redis.io), a distributed key-value store, using the [aioredis](https://github.com/aio-libs/aioredis) library. How would we make a Redis connection available to views?

The naive solution would be to create a `redis` global variable, initially `None`, and then use [lifespan handlers](/guide/apps.md#lifespan-events) to give it a value on app startup. It's hacky, and definitely not very testable. Instead, let's use providers!

Let's start by adding a `REDIS_URL` setting to the settings module:

```python
# myproject/settings.py
from starlette.config import Config

config = Config(".env")

PROVIDERS_MODULES = ["myproject.providerconf"]
REDIS_URL = config("REDIS_URL", default="redis://localhost")
```

We can now define the `redis` provider. Since we registered `myproject.providerconf` in `PROVIDERS_MODULES`, let's place the provider there:

```python
# myproject/providerconf.py
import aioredis
from bocadillo import provider, settings

@provider
async def redis():
    conn = await aioredis.create_redis(settings.REDIS_URL)
    yield conn
    await conn.wait_closed()
```

Thanks to this code, if a request is made to your application, and the view asked for the `redis` provider (more on that shortly), here's what happens:

1. Bocadillo executes everything above the `yield` statement. In this case, it connects to Redis and creates the connection object.
2. The `yield`ed object (here, the Redis connection) is passed to the view as a keyword argument.
3. When the view has finished (and even if an exception occurred), Bocadillo executes everything after the `yield` statement. In this case, it closes the Redis connection.

::: tip
It is not mandatory that a provider uses `yield`. If no cleanup is required, it can also simply `return`:

```python
@provider
async def hello():
    return "Hello, world!"
```

:::

Now, how can we use the `redis` provider in a view?

Simple enough: **by declaring it as a view parameter**.

```python
# myproject/app.py
@app.route("/value")           👇
async def get_value(req, res, redis):
    value = await redis.get("some-key")
    if value is None:
        value = 42
        await redis.set("some-key", value)
    res.json = {"value": value}
```

An important principle behind providers is _Define once, reuse everywere_: we could also access the Redis cache in other REST endpoints, or in a WebSocket endpoint:

```python
# myproject/app.py
@app.route("/valuefeed")  👇
async def value_feed(ws, redis):
    async for message in ws:
        value = await redis.get(message["key"])
        await ws.send({"value": value})
```

::: tip SEE ALSO
The [tutorial](/guide/tutorial.md) shows how to use providers and WebSocket to implement a real-time chatbot server.
:::

## Scopes

By default, a provider is computed on each request. But some providers are typically expansive to setup and teardown, or could gain from being reused across requests. In the previous example, we may want to reuse the Redis connection throughout the lifespan of the application.

For this reason, Bocadillo providers have two possible **scopes**:

- `request`: a new copy of the provider is computed for each HTTP request or WebSocket connection. This is the default behavior.
- `app`: the provided value is reused and shared between requests.

The `app` scope can be used to implement **long-lived objects**, i.e. objects which Bocadillo initialises and reuses for as long as the app is running.

For example, you could keep track of connected WebSocket clients via an app-scoped provider which initially returns an empty set:

```python
# myproject/providerconf.py
from bocadillo import provider

@provider(scope="app")
async def clients() -> set:
    return set()
```

and then register/unregister clients as they connect/disconnect to the WebSocket endpoint:

```python
# myproject/app.py
@app.websocket_route("/echo")
async def echo(ws, clients: set):
    clients.add(ws)
    try:
        async for message in ws:
            await ws.send(message)
    finally:
        clients.remove(ws)
```

## Modularity

Providers are **modular**, in the sense that **providers can be injected into other providers**. This allows to build an ecosystem of loosely-coupled, reusable resources.

A contrived example of this could be:

```python
# myproject/providerconf.py
from bocadillo import provider

@provider
async def message_format():
    return "{greeting}, {who}"

@provider
async def hello_message_format(message_format):
    return message_format.format(greeting="Hello")
```

As you can see, `hello_message_format` reuses the `message_format` provider.

## Auto-used providers

If you want the provider to be activated without explicitly declaring it as a parameter of a view, use `autouse=True`.

For example, you can make sure that database calls are always performed within a transaction. Using the [Databases](https://github.com/encode/databases) library, this could be implemented by creating a `db` provider first:

```python
# myproject/providerconf.py
from databases import Database
from bocadillo import provider

@provider(scope="app")
async def db() -> Database:
    async with Database("sqlite://:memory:") as db:
        yield db
```

And then creating another **auto-used provider** which automatically sets up a transaction:

```python
# myproject/providerconf.py
@provider(autouse=True)
async def transaction(db: Database):
    async with db.transaction():
        yield
```

## Decorator usage

If you don't actually need the value returned by the provider, you can decorate the consumer view with the `@useprovider` decorator:

```python
# myproject/providerconf.py
@provider(name="show_hello")
async def provide_show_hello():
    print("Hello, providers!")
```

```python
# myproject/app.py
@app.route("/hi")
@useprovider("show_hello")
async def say_hi(req, res):
    res.text = "A hello message was printed to the console."
```

::: tip

- The `@useprovider` decorator accepts a variable number of providers.
- Providers can be passed by name or by reference.

:::

## Factory providers

Factory providers are a **design pattern** that allows to build generic providers that can be used for a variety of inputs.

tl;dr: instead of returning a value, the provider returns a **function**.

As an example, let's build a factory provider that retrieves a note item from the database given its primary key. We'll use a hardcoded in-memory database of sticky notes for the sake of simplicity:

```python
# myproject/providerconf.py
from bocadillo import provider

@provider(scope="app")
async def notes():
    # TODO: get these from a database
    return [
        {"id": 1, "text": "Groceries"},
        {"id": 2, "text": "Make potatoe smash"},
    ]

@provider
async def get_note(notes):
    async def _get_note(pk: int) -> dict:
        note = next(note for note in notes if note["id"] == pk, None)
        if note is None:
            raise HTTPError(404, detail=f"Note with ID {pk} does not exist.")
        return note

    return _get_note
```

Example usage:

```python
# myproject/app.py
@app.route("/notes/{pk}")
async def retrieve_note(req, res, pk: int, get_note):
    res.json = await get_note(pk)
```

## How are providers discovered?

Bocadillo can find providers from a number of sources:

1. **(Recommended)** Functions decorated with `@provider` that live in a module listed in the `PROVIDERS_MODULES` setting. This is what [Bocadillo CLI](https://github.com/bocadilloproject/bocadillo-cli) generates.

```python
# myproject/settings.py
PROVIDERS_MODULES = ["myproject.providerconf", "myproject.more_providers"]
```

2. Functions decorated with `@provider` that live in a module marked for discovery using `discover_providers()`.

```python
# myproject/app.py
from bocadillo import discover_providers

discover_providers("myproject.more_providers")
```

3. Functions decorated with `@provider` that live in a `providerconf.py` module relative to the current working directory (note that this may be different from the directory where `app.py` is located).

```python
# providerconf.py
import random as _random
from bocadillo import provider

@provider
async def random() -> float:
    return _random.random()
```

4. Functions decorated with `@provider` present in the application script:

```python
# myproject/app.py
from bocadillo import App, provider

@provider
async def message():
    return "Hello, providers!"

app = App()

@app.route("/hello")
async def hello(req, res, message):
    res.json = {"message": message}
```

5. Functions decorated with `@provider` that get _imported_ in the application script:

```python
# myproject/messages.py
from bocadillo import provider

@provider
async def message():
    return "Hello, providers!"
```

```python
# myproject/app.py
from . import messages
```

## Naming providers <Badge text="Advanced" type="warn"/>

By default, a provider's name is the same as that of its defining function, but you can override it with the `name` parameter to `@provider`.

When the provider is declared and used _in the same file_, linters and IDEs may complain because of conflicting names. A good convention is then to name the provider function as `provide_{name}`. For example:

```python
@provider(name="hello")
async def provide_hello():
    return "Hello, providers!"
```

## Lazy evaluation <Badge text="Advanced" type="warn"/>

By default, Bocadillo awaits the coroutine returned by the provider before passing it to the view. (Note: if this is gibberish, take a look at the [Async crash course](/guide/async.md).)

If you need to defer awaiting the provider until you really need it, you can declare it as `lazy`. The following example uses the [requests-async](https://github.com/encode/requests-async) library:

```python
# myproject/providerconf.py
import requests_async as requests
from bocadillo import provider

@provider(lazy=True)
async def random_data():
    r = await requests.get("https://httpbin.org/json")
    return r.json()
```

```python
# myproject/app.py
@app.route("/data")
async def get_data(req, res, random_data: Awaitable[dict]):
    res.json = random_data
```

::: warning CAVEAT
Lazy providers can only be **request-scoped**. If they could be app-scoped, Bocadillo would have no way to know whether it has already been awaited when processing another request.
:::
