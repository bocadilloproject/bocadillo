# Databases

Storing data and/or retrieving it from a database is a very common task to perform in a server-side web application.

**Bocadillo does not provide its _own_ database layer**, and probably never will. However, we do wish to integrate with a recommended solution in a foreseeable future.

In the meantime, you'll need to integrate with third-party libraries. While doing so, you'll definitely find [providers] handy, as shown in this guide.

[providers]: /guide/providers.md

::: tip NOTE
**Querying a database is typically I/O-bound** and can represent a significant part of the request processing time.

This makes **asynchronous programming** an ideal tool for the job, which is why this page only discusses **async solutions**.
:::

## SQL

### Databases

[databases]: #databases-2

[Databases](https://github.com/encode/databases) is a library that "brings async database support to Python". It was built by Tom Christie, the developer behind the Django REST Framework, Starlette, uvicorn, as well as a number of exciting projects in the async Python world.

Here's an example setup that uses [providers] to create the Database instance and inject it into web views:

```python
# providerconf.py
from bocadillo import provider
from databases import Database

@provider(scope="app")
async def db():
    async with Database("postgresql://localhost/example") as db:
        yield db
```

```python
# app.py
from bocadillo import App

app = App()

@app.route("/")
async def index(req, res, db):
    # TODO: query the `db`! ✨
    ...
```

### ORM

Using an ORM (Object Relational Mapper) allows you to think in terms of classes and objects instead of tables and rows.

This technique has [a number of benefits and drawbacks](https://www.fullstackpython.com/object-relational-mappers-orms.html), but if you go for it the recommended option is [orm], an asynchronous ORM for Python. It's based on SQLAlchemy Core, so it's fast, and easy to use, and supports all major databases (PostgreSQL, MySQL and SQLite). Besides, you can integrate it with Bocadillo to get **data validation** without any boilerplate — see: [Use orm to interact with an SQL database](/how-to/orm.md).

[orm]: https://github.com/encode/orm

For completeness, here are some alternatives to `orm` we've come across:

- [Tortoise]: an async ORM inspired by the Django ORM.
- [GINO]: an async ORM based on SQLAlchemy Core.
- [peewee-async]: async wrapper around [peewee].

[tortoise]: https://tortoise-orm.readthedocs.io
[gino]: https://github.com/fantix/gino
[peewee-async]: https://github.com/05bit/peewee-async
[peewee]: https://github.com/coleifer/peewee

### Dialect-specific client library (advanced)

If your use case is very specific or low-level, you may want to resort to a dialect-specific async client library.

Here are some of the most popular ones:

- [asyncpg] for PostgreSQL.
- [aiomysql] for MySQL.
- [aiosqlite] for SQLite.

[asyncpg]: https://www.github.com/MagicStack/asyncpg
[aiomysql]: https://github.com/aio-libs/aiomysql
[aiosqlite]: https://github.com/jreese/aiosqlite

Again, you'll definitely want to use [providers] to setup and teardown database connections. Here's an example for asyncpg:

```python
# providerconf.py
import asyncpg
from bocadillo import provider

@provider(scope="app")
async def conn():
    conn = await asyncpg.connect(
        user="user", password="secret", database="example", host="localhost"
    )
    yield conn
    await conn.close()
```

## NoSQL

If you're using a NoSQL database, many high-quality async clients are already available.

Here are some popular ones:

- [Motor](https://github.com/mongodb/motor) for MongoDB.
- [aioelasticsearch](https://github.com/aio-libs/aioelasticsearch) for ElasticSearch.
- [aioredis](https://github.com/aio-libs/aioredis) for Redis.

You can find an example Redis setup [at the end of the providers problem statement](/guide/providers.md#problem-with-providers).
