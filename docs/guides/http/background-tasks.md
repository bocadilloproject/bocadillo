# Background tasks

Sometimes, you may want to perform further processing after handling a request, but without making the client wait for the result. Examples of this include sending emails or dumping logs to a remote system.

Background tasks address this exact use case.

## How do background tasks work?

A background task is a no-argument asynchronous function, i.e. one similar to:

```python
async def do_stuff():
    pass
```

which is attached to a [Response] object.

When registered, the background task won't run immediately. Instead, the view will terminate as usual and **the background task will execute after the response has been sent**. This means that the client will effectively not wait for the background task to finish before getting a response.

In the meantime, the server will still be able to process other requests while the background task executes — provided the task is non-blocking (see [Caveats](#caveats)).

## Creating a background task

To create a background task, decorate a no-argument async function with `@res.background` inside a view.

Here's an example that simulates sending a confirmation email:

```python
from asyncio import sleep
from bocadillo import API, view

api = API()

@api.route("/orders")
@view(methods=["post"])
async def create_order(req, res):
    @res.background
    def send_confirmation():
        # TODO: send an email here
        await sleep(1)

    res.status_code = 201
```

## Parametrized tasks

You can also use `res.background()` as a regular function. This is useful to define parametrized tasks. Extra arguments or keyword arguments passed to `res.background()` will be passed to the task function.

```python
from asyncio import sleep
from bocadillo import API, view

api = API()

async def send_confirmation(who: str):
    # TODO: send an email here
    await sleep(1)

@api.route("/orders")
@view(methods=["post"])
async def create_order(req, res):
    res.background(send_confirmation, "user@example.net")
    res.status_code = 201
```

## Caveats

### Background tasks must be non-blocking

A background task is executed concurrently, *not* in parallel. This means that you should avoid performing blocking calls or CPU-bound operations because they would block the whole server too.

In the email example above, this means you should use an asynchronous, non-blocking email backend. A potential option is [aiosmtpd](https://github.com/aio-libs/aiosmtpd).

### Multiple background tasks aren't supported

Only the latest task registered via `@res.background` will execute — previous ones are simply discarded.

If you need to perform multiple things concurrently (e.g. send multiple emails), you should resort to [`asyncio.gather()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather) instead.

[Response]: ../http/responses.md
