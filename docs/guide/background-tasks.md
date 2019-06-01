# Background tasks

Background tasks are a lightweight mechanism to perform processing after a request has been sent, without making the client wait for the result. Typical examples include sending email, or sending logs to a remote system.

## How do background tasks work?

When registered on the [Response](/guide/responses.md), the background task won't run immediately. Instead, the view will terminate as usual, and the response will be sent. Only then, the background task will execute.

This prevents clients from waiting for the background task to finish before getting a response.

In the meantime, the server will still be able to process other requests while the background task executes — provided the task is non-blocking (see [Caveats](#caveats)).

## Creating a background task

To create a background task, decorate a no-argument async function with `@res.background` inside a view.

Here's an example that simulates sending a confirmation email:

```python{9-12}
from asyncio import sleep
from bocadillo import App, view

app = App()

@app.route("/orders", methods=["post"])
async def create_order(req, res):
    @res.background
    def send_confirmation():
        # TODO: send an email here
        await sleep(1)

    res.status_code = 201
```

## Parametrized tasks

You can also use `res.background()` as a regular function: extra arguments or keyword arguments will be passed to the task function. This is useful to define **reusable parametrized tasks**.

```python{6-8,13}
from asyncio import sleep
from bocadillo import App, view

app = App()

async def send_confirmation(who: str):
    # TODO: send an email here
    await sleep(1)

@app.route("/orders", methods=["post"])
async def create_order(req, res):
    res.background(send_confirmation, who="user@example.net")
    res.status_code = 201
```

## Caveats

- **Background tasks must be non-blocking.**

Because a background task is a coroutine, it must be non-blocking to avoid blocking the main thread and preventing requests from being processed.

As described in the [Async crash course](/guide/async.html#finding-async-libraries-to-replace-synchronous-ones), this means you should use asynchronous libraries. In the email example above, we could use [aiosmtpd](https://github.com/aio-libs/aiosmtpd).

If you're unable to write an async-native background tasks, use one of the techniques described in [Executing CPU-bound operations](http://localhost:8080/guide/async.html#common-patterns).

- **Multiple background tasks aren't supported.**

Only the latest task registered via `@res.background` will execute — previous ones are simply ignored.

If you need to perform multiple things concurrently (e.g. send multiple emails), you should resort to [`asyncio.gather()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather) instead.
