# Databases

Storing data and/or retrieving it from a database is a very common task to perform in a server-side web application.

**Bocadillo does not provide its _own_ database layer**, and probably never will. However, we do wish to integrate with a recommended solution in a foreseeable future.

In the meantime, you'll need to integrate with third-party libraries. While doing so, you'll definitely find [providers] handy, as shown in this guide.

[providers]: /guides/injection/

::: tip NOTE
**Querying a database is typically I/O-bound** and can represent a significant part of the request processing time.

This makes asynchronous programming an ideal tool for the job, which is why this page only discusses **async solutions**.
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

if __name__ == "__main__":
    app.run()
```

### ORM

Using an ORM (Object Relational Mapper) allows you to think in terms of classes and objects instead of tables and rows. You should be aware that this has [a number of benefits and drawbacks](https://www.fullstackpython.com/object-relational-mappers-orms.html).

There are awesome things happening in the landscape of Python async ORMs right now. Here are some of the best alternatives we've come across:

- [orm]: an async ORM built on top of [Databases]. It has support for Postgres, MySQL, and SQLite and exposes a Django-like querying interface.
- [Tortoise]: an async ORM inspired by the Django ORM. See also our [Tortoise guide](/how-to/tortoise.md).
- [GINO]: an async ORM based on SQLAlchemy Core.
- [peewee-async]: async wrapper around [peewee].

[tortoise]: https://tortoise-orm.readthedocs.io
[orm]: https://github.com/encode/orm
[gino]: https://github.com/fantix/gino
[peewee-async]: https://github.com/05bit/peewee-async
[peewee]: https://github.com/coleifer/peewee

Our recommended option is the `orm` package. It's beautiful, ease to use, and _very_ easy to integrate with Bocadillo. Beware, though, that the project is still very young, so make sure to pin your dependencies.

Anyway, here's an example setup:

```python
# db.py
import os

import databases
import orm
import sqlalchemy

url = os.getenv("DATABASE_URL")
database = databases.Database(url)
metadata = sqlalchemy.MetaData()

class Post(orm.Model):
    __tablename__ = "posts"
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    title = orm.String(max_length=300)
    content = orm.Text(allow_blank=True)

engine = sqlalchemy.create_engine(url)
metadata.create_all(engine)
```

```python
# app.py
from bocadillo import App
from db import Post

app = App()

@app.route("/posts")
async def list_posts(req, res):
    res.media = [dict(post) for post in await Post.objects.all()]

if __name__ == "__main__":
    app.run()
```

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

You can find an example Redis setup [at the end of the providers problem statement](/guides/injection/problem.md#with-providers).
