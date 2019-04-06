# Basics

## Registering a provider

Registering a provider can be done by decorating a function with the `@bocadillo.provider` decorator.

Here's a simple hello world provider:

```python
from bocadillo import provider

@provider
def hello() -> str:
    return "Hello, dependency injection!"
```

Some terminology:

- The `hello()` function itself is called a **provider function**.
- A provider function decorated with `@provider` is called a **provider**.

### Naming providers

By default, a provider's name is the same as its provider function's. In the above example, the resulting provider would be named `"hello"`:

```python
>>> hello.name
"hello"
```

When the provider is declared and used _in the same file_, linters and IDEs may complain because of conflicting names. So, if you ever need it, you can explicitly specify a provider's name with the `name` parameter. A good convention is then to name the provider function as `provide_{name}`. For example:

```python
@provider(name="hello")
def provide_hello():
    return "Hello, dependency injection!"
```

## Using a provider

### As a view parameter

Once the provider has been defined, it can be used in views by declaring it as a parameter of the view function.

- HTTP example:

```python
@app.route("/hi")
async def say_hi(req, res, hello: str):
    res.text = hello
```

- HTTP example (class-based):

```python
@app.route("/hi")
class SayHi:
    async def get(self, req, res, hello: str):
        res.text = hello
```

- WebSocket example:

```python
@app.websocket_route("/hi")
async def say_hi(ws, hello: str):
    await ws.send(hello)
```

::: tip NOTE
The examples above use an `str` type annotation for the `hello` parameter. This has nothing to do with providers, and isn't used to determine which providers need to be injected. Only the name of the parameter matters.
:::

### As a decorator

Alternatively, you can decorate a view with the `@useprovider` decorator. This is useful when you don't need to use the value returned by the provider.

```python
from bocadillo import provider, useprovider

@provider
def hello():
    print("Hello, providers!")

@app.route("/hi")
@useprovider("hello")
async def say_hi(req, res):
    res.text = "A hello message was printed to the console."
```

::: tip

- The `@useprovider` decorator accepts a variable number of providers.
- Providers can be passed by name or by reference.

:::

## How are providers discovered?

Bocadillo can discover providers from the following sources:

1. Functions decorated with `@provider` present in the application script.

```python
# app.py
from bocadillo import provider

@provider
def message():
    return "Hello, providers!"

app = App()

@app.route("/hello")
async def hello(req, res, message):
    res.media = {"message": message}
```

2. Functions decorated with `@provider` that get _imported_ in the application script.

```python
# notes.py
from bocadillo import provider

class Note:
    def __init__(self, id: int, text: str):
        self.id = id
        self.text = text

@provider
def example_note() -> Note:
    return Note(id=1, text="Cook mashed potatoes")
```

```python
# app.py
from notes import Note  # => `example_note` discovered
```

3. Functions decorated with `@provider` that live in a `providerconf.py` module relative to the application script.

```python
# providerconf.py
import random as _random
from bocadillo import provider

@provider
def random() -> float:
    return _random.random()
```

4. Functions decorated with `@provider` that live in a module marked for discovery in the application script using `bocadillo.discover_providers(*module_paths)`.

```python
# app.py
from bocadillo import discover_providers

discover_providers("notes")  # => `example_note` discovered
```
