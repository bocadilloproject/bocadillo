# Problem statement

Before we discuss how to use providers, let's see what kind of problem they were made to solve exactly.

::: tip TL;DR:
Providers help you **decouple resources from their consumers**. Using providers typically results in an application being much **easier to test, change and maintain**. No big deal!
:::

## Example: caching powered by Redis

Suppose we're implementing a caching system backed by [Redis](https://redis.io), a key-value store, using the [aioredis](https://github.com/aio-libs/aioredis) library.

The application would connect to the Redis instance on startup, disconnect on shutdown (see [event handlers](../agnostic/events.md)), and views could use the connection object to cache items to Redis.

## Without providers

Let's see how this would look like:

```python
# app.py
import aioredis
from bocadillo import App, Templates

app = App()
templates = Templates()

# Initialise the redis reference, which will be set on app startup.
redis = None

@app.on("startup")
async def connect():
    nonlocal redis
    redis = await aioredis.create_redis("redis://localhost")

@app.on("shutdown")
async def disconnect():
    await redis.wait_closed()
    redis = None

# Use the redis instance to cache a rendered HTML page.
@app.route("/")
async def index(req, res):
    page = await redis.get("index-page")
    if page is None:
        page = await templates.render("index.html")
        await redis.set("index-page", page)
    res.text = page

if __name__ == "__main__":
    app.run()
```

This code may look fine at first sight, but there are at least two issues:

1. The global `redis` variable makes this code very hard to test. We cannot easily swap the live Redis connection for another implementation (e.g. a mock).
2. The code is cluttered by logic related to provisioning the Redis connection.

To solve 2), you may think about abstracting the event handlers away using an [ASGI middleware](../agnostic/asgi-middleware.md):

```python
# cache.py
import aioredis
from bocadillo import ASGIMiddleware

class RedisCache(ASGIMiddleware):

    def __init__(self, inner, app, url: str = "redis://localhost"):
        super().__init__(inner, app)

        self.redis = None
        self.url = url

        @app.on("startup")
        async def connect():
            self.redis = await aioredis.create_redis(self.url)

        @app.on("shutdown")
        async def disconnect():
            if self.redis is not None:
                await self.redis.wait_closed()
```

But this approach wouldn't work in practice, because now we cannot reference the `redis` instance from the application script — it's confined within the middleware!

(You could add a dynamic `.redis` attribute to `app`, but we argue that this is not satisfactory nor scalable. For example, it doesn't work well with type annotations.)

Also, consider this: what if the routes were declared in a separate [recipe](../agnostic/recipes.md)? How could we make sure they use the same cache? This would be even more problematic if the cache was in-memory — we wouldn't want to have the recipe and the app reference different copies of the cache!

## With providers

As you surely begin to feel, _there must be a better way_… And surely enough, there is: [dependency injection](https://en.wikipedia.org/wiki/Dependency_injection), of which providers are an implementation.

As a teaser, here's how providers can allow us to implement beautiful, testable code for providing a Redis instance to our application:

1. Define a `redis` provider in `providerconf.py`:

```python
# providerconf.py
import aioredis
from bocadillo import provider

@provider(scope="app")
async def redis():
    redis = await aioredis.create_redis("redis://localhost")
    yield redis
    await redis.wait_closed()
```

2. Use it in a view:

```python
# app.py
from bocadillo import App, Templates

app = App()
templates = Templates()

@app.route("/")
async def index(req, res, redis):
    page = await redis.get("index-page")
    if page is None:
        page = await templates.render("index.html")
        await redis.set("index-page", page)
    res.text = page

if __name__ == "__main__":
    app.run()
```

That's it! As you can see, providers allow views to **receive and use objects without having to care about import, setup nor cleanup**.

Let's now see what features providers offer and how to use them.
