# Yield providers

Some providers need to perform cleanup operations when they go out of scope. For example:

- a request-scoped file provider may need to close descriptors when the request has been processed.
- an app-scoped database provider may need to close the open connections when the app shuts down.

To support this, Bocadillo providers support using a `yield` statement instead of `return`. The yielded value will be injected in the view, and all the code after the `yield` statement (also known as _finalization code_) will be executed when cleaning up the provider.

Such providers are called **yield providers**.

## Example: providing a writable file

As an example, here's a provider for a log file that views can append lines to:

```python
from datetime import datetime
from bocadillo import App, provider

@provider
def log():
    logfile = open("/var/requests.log", "w+")
    yield logfile
    logfile.close()

app = App()

@app.route("/")
async def index(req, res, log):
    log.write(f"{datetime.now()}: {req.client.host}")
    res.text = "Hello, yield providers"
```

::: tip
Teardown code will be executed even if an exception occurs within the view. You don't have to wrap the `yield` within a `try/finally` block.
:::

Yield providers also play nicely with `with` statements:

```python
@provider
def log():
    with open("/var/requests.log", "w+") as logfile:
        yield logfile
```

## App-scoped yield providers

Yield providers that are also [app-scoped](./scopes.md) work really well when you need to provide an expensive resource for the whole lifetime of the application. This pattern is an alternative to traditional [event handlers](/guides/architecture/events.md) for when you need the event handler to setup a resource that views can use.

The reason why this works is because:

- App-scoped providers are instanciated on application startup (as for all providers).
- _And_ the finalization code of app-scoped yield providers is executed on application shutdown.

As an example, here is how you could provide a database connection using the [Databases](https://github.com/encode/databases) library:

```python
from bocadillo import provider
from databases import Database

@provider(scope="app")
async def db():
    async with Database("sqlite://:memory:") as database:
        yield database
```

With this code, the application would connect to the SQLite database on startup, and disconnect on shutdown.
