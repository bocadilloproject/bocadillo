# Async crash course

New to asynchronous programming in Python? Fear not! This crash course will get you up and running with async and how it impacts building web applications.

If you're already comfortable with async, feel free to skip to the [tutorial](/guide/tutorial.md).

We'll keep this short, to the point, and focused on using async in Bocadillo. To learn more, see [Resources for aspiring experts](#resources-for-aspiring-experts) at the bottom of this page.

## TL;DR

- **Defining an async function**: use `async def` instead of `def`.
- **Calling an async function**: use the `await` keyword _inside an async function_: `value = await func()`.
- **CPU-bound operations**: use the `starlette.concurrency.run_in_threadpool` helper.
- **Async libraries**: check out [awesome-asyncio] or do your own research!

## Terminology

### Synchronous function

Also known as a _regular function_, this is just a standard Python function defined using the `def` syntax:

```python
def get_attendees():
    return ["John", "Mary", "Isabella"]
```

### Asynchronous function

Also known as a _coroutine function_, an asynchronous function returns a [coroutine](#coroutine) and is defined using the `async def` syntax:

```python
async def get_attendees():
    return ["John", "Mary", "Isabella"]
```

### Awaitable

An awaitable is an object which can be used in an `await` expression. The term "awaitable" is really not much more than a syntax-level definition.

### Coroutine

The return value of an [asynchronous function](#asynchronous-function) is a particular kind of [awaitable](#awaitable) known as a **coroutine**.

Coroutines are first-class citizens in Python. There's even a built-in type for them! Here, take a look:

```python
async def get_attendees():
    return ["John", "Mary", "Isabella"]

coro = get_attendees()
print(type(coro))  # <class 'coroutine'>
```

## Working with coroutines

### Basics

Consider the following asynchronous function:

```python
async def get_items():
    print("Getting items…")
    return [1, 2, 3]
```

Let's call it:

```python
items = get_items()
```

At this point, `items` is a [coroutine](#coroutine):

```python
print(type(items))  # <class 'coroutine'>
```

Have you noticed that "Getting items…" has not been printed yet? This is because `get_items()` has not even _run_ yet!

"But then", you say, "how do I run the coroutine and get its result?"

Good question. Here's an inaccurate but pragmatic answer\*:

1. Make sure you are in an [asynchronous function](#asynchronous-function), i.e. one defined with `async def`.
2. Use the `await` syntax.

Here's what it looks like:

```python
async def main():  # <- example async function
    items = await get_items()  # <- call another async function with `await`
    print(items)  # [1, 2, 3]
```

_\*If you're curious to know the more accurate answer, you'll find a lot of useful information in the [asyncio documentation](https://docs.python.org/3/library/asyncio.html), e.g. in [Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html)._

"But then", you say, "how am I supposed to run `main()`?!"

Well, you don't, because…

### Async is the interface

As an async web framework, Bocadillo provides an _asynchronous runtime_ and takes care of running coroutines for you. This allows you to write `async/await` code without worrying about who runs it and how.

If that sounds confusing, take a look at the following "Hello, World" application:

```python
from bocadillo import App, configure

app = App()
configure(app)

@app.route("/")
async def hello(req, res):
    res.text = "Hello, world!"
```

This code doesn't care about how the `hello` function is actually run. You don't even need to know anything about `asyncio` or how it works.

You just need to use the `async def` syntax on the view, and Bocadillo will do the heavy lifting to handle requests in a concurrent fashion. It's magic. ✨

### Summary

To sum up, here's the gist of what you need to know when working with asynchronous functions and coroutines in Bocadillo:

- Define an asynchronous function\* using `async def func(): ...`.
- Call an asynchronous function\* and get its result using `value = await func()`.
- Bocadillo provides the asynchronous runtime so you can focus on writing async code instead of worrying about how it should run.

_\*A view, an error handler, a hook, an HTTP middleware callback, etc._

## Common patterns

Here are a few patterns you may find useful while working with async code.

### Executing CPU-bound operations

In Python, async relies on _cooperative multitasking_. This means that if a function puts high load on the CPU without using `await`, other coroutines won't be able to run in the meantime, and you'll lose concurrency.

In a web context in particular, this means that clients need to wait for said function to terminate before they can get their request processed.

To solve this issue, you can use Starlette's `run_in_threadpool` helper. It will run the function in a separate thread to ensure that the main thread (where coroutines are run) does not get blocked.

Here's an example of running an expensive CPU-bound operation (sorting random numbers) in a view using `run_in_threadpool`:

<<<@/docs/guide/snippets/work_check.py

Try it out for yourself:

1. Start the server: `uvicorn app:app`
2. Create two new terminal sessions.
3. In the first terminal, run the following to start sorting 10^7 random numbers:

```bash
curl http://localhost:8000/work/7
```

4. In the second terminal, run the following while the first terminal is still waiting for a response:

```bash
curl http://localhost:8000/check
```

You should be able to get `OK` responses in the second terminal even though the server is still sorting numbers. This is because the sort happens in a separate thread — concurrency is preserved! 🎉

### Converting a regular function to an asynchronous function

If you're given a regular function and you need to convert it to an asynchronous function, you can just write an async wrapper:

```python
from somelib import compute

async def compute_async(*args, **kwargs):
    return compute(*args, **kwargs)
```

**Note**: if `compute` is CPU-bound, wrapping it in an `async` function won't magically prevent it from blocking the main thread — you need to use `run_in_threadpool` as well:

```python
from starlette.concurrency import run_in_threadpool
from somelib import compute

async def compute_async(*args, **kwargs):
    return await run_in_threadpool(compute, *args, **kwargs)
```

This can be simplified using `functools.partial`:

```python
from functools import partial
from starlette.concurrency import run_in_threadpool
from somelib import compute

compute_async = partial(run_in_threadpool, compute)
```

### Finding async libraries to replace synchronous ones

One of the caveats associated to async is that _everything_ needs to be asynchronous (a.k.a. non-blocking), or you may block the main thread and lose concurrency.

For this reason, you will need to use async equivalents of your favorite libraries if they don't support async natively.

For example:

- [Databases](https://github.com/encode/databases) instead of [SQLAlchemy](https://www.sqlalchemy.org/).
- [requests-async](https://github.com/encode/requests-async) instead of [requests](http://docs.python-requests.org/en/master/).

You can check out [awesome-asyncio], [Libraries that work with async/await](https://realpython.com/async-io-python/#libraries-that-work-with-asyncawait) or do your own research to find async libraries. The ecosystem is ever evolving — be on the lookout!

## Resources for aspiring experts

If you're curious to learn more about async in Python — the history, the implementation, the ecosystem — here are a few resources we think you'll find useful.

Talks:

- [Asynchronous Python for the Complete Beginner](https://www.youtube.com/watch?v=iG6fr81xHKA) - Miguel Grinberg, PyCon 2017.
- [Async/await in Python 3.5 and why it is awesome](https://www.youtube.com/watch?v=m28fiN9y_r8&t=132s) - Yury Selivanov, EuroPython 2016.

Writings:

- [Async IO in Python: A Complete Walkthrough](https://realpython.com/async-io-python/) - Real Python.

Lists:

- [aio-libs](https://github.com/aio-libs) - The set of asyncio-based libraries built with high quality.
- [awesome-asyncio] - A curated list of awesome Python asyncio frameworks, libraries, software and resources.

[awesome-asyncio]: https://www.github.com/timofurrer/awesome-asyncio

References:

- [Official asyncio documentation](https://docs.python.org/3/library/asyncio.html) - A library to write concurrent code using the async/await syntax.
- [ASGI](https://asgi.readthedocs.io/en/latest/) - Asynchronous Server Gateway Interface.

[awesome-asyncio]: https://www.github.com/timofurrer/awesome-asyncio
