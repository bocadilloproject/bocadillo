# Interact with an SQL database with Tortoise ORM

Relational databases are a robust, well-established and convenient way to
persist and query application data.

This guide will guide you through the steps of integrating [Tortoise ORM][tortoise] into your project to interact with an SQL database asynchronously.

## Introduction

### What is an ORM?

Paraphrasing the [Wikipedia page][orm-wikipedia], ORM — a.k.a. *Object Relational Mapping* — is a programming technique to convert data between incompatible type systems.

Although it is a general concept, *an ORM* typically refers to software that acts as **a conversion layer between a given programming language and a database**, e.g. between Python and PostgreSQL.

Put simply, an ORM allows the developer to interact with the database through objects and method calls instead of writing SQL queries by hand.

### Do I need an ORM?

Using an ORM has the benefit of making the data manipulation code more reusable, more consistent and more secure.

That said, keep in mind that ORMs have downsides, too. [Full Stack Python's article on Object Relation Mappers][fsp-article] mentions impedance mismatch, potentially reduced performance, and shift of complexity from the database to application code.

Depending on your use case, you may get away with using an async SQL client such as:

- [asyncpg] for PostgreSQL.
- [aiomysql] for MySQL.
- [aiosqlite] for SQLite.

### Why not SQLAlchemy?

[SQLAlchemy] is a very popular Python ORM, commonly used in conjonction with a microframework such as [Flask], [Falcon] or similar.

The main issue with SQLAlchemy in the context of asynchronous web servers is that it is *synchronous*. This means that while the query is being executed, the server will block while it is waiting on I/O.

In fact, querying a database is almost always an I/O-bound operation. This makes asynchronous programming a very suitable paradigm for interacting with databases.

### Why Tortoise ORM?

Because it is async-first, just like Bocadillo.

Implementations of async Python ORMs rely on the recent development of async Python database clients (such as [asyncpg] or [aiomysql]).

A popular approach has been to map synchronous ORMs to be asynchronous. This is the case of [GINO][gino], built on top of SQLAlchemy Core, or [peewee-async], built on top of [peewee].

On the other hand, [Tortoise ORM][tortoise] is a from-scratch ORM implementation specifically targeted at async Python applications. It exposes a clean API very reminiscent of the Django ORM.

### What about NoSQL?

If you're using NoSQL, you don't need an ORM and — luckily — many high-quality async clients are already available, such as:

- [Motor] for MongoDB.
- [aioelasticsearch] for ElasticSearch.
- [aioredis] for Redis.

## Integrating Tortoise ORM

1. Install Tortoise itself:

```bash
pip install tortoise-orm
```

2. Tortoise comes with [aiosqlite] by default, but if you're using another database than SQLite, install the adequate async driver among [those supported by Tortoise][tortoise-db-backends], e.g. [asyncpg]:

```bash
pip install asyncpg
```

3. Register startup and shutdown [event handlers][events] to initialize and clean up database connection (see also [Set up (Tortoise)][tortoise-setup]):

```python
from bocadillo import API
from tortoise import Tortoise

api = API()


@api.on("startup")
async def db_init():
    await Tortoise.init(
        # Connect to a database located at `$DATABASE_URL`,
        db_url=os.environ["DATABASE_URL"],
        # Register the `models.py` file to be discovered for models.
        # The dict key will be used as a namespace to reference models,
        # e.g. when setting up relationships.
        modules={"models": ["models"]}
    )
    # Generate the schema
    await Tortoise.generate_schemas()


@api.on("shutdown")
async def db_cleanup():
    await Tortoise.close_connections()
```

There are no additional integration steps. Once this is done, you can start using Tortoise as described in the official documentation. We recommend you follow the [Tortoise Getting Started guide][tortoise-getting-started] to get the ground running.

## Bloguero: a basic blog example

Bloguero is an example blog app that makes use of Tortoise to store blog posts.

The full code for this application can be found [on GitHub][bloguero].

<<<@/docs/how-to/database/snippets/models.py

<<<@/docs/how-to/database/snippets/blog.py

[orm-wikipedia]: https://en.wikipedia.org/wiki/Object-relational_mapping
[tortoise]: https://tortoise-orm.readthedocs.io/en/latest/
[flask]: http://flask.pocoo.org
[falcon]: https://falcon.readthedocs.io
[sqlalchemy]: https://www.sqlalchemy.org
[asyncpg]: https://www.github.com/MagicStack/asyncpg
[aiomysql]: https://github.com/aio-libs/aiomysql
[aiosqlite]: https://github.com/jreese/aiosqlite
[fsp-article]: https://www.fullstackpython.com/object-relational-mappers-orms.html
[gino]: https://github.com/fantix/gino
[peewee-async]: https://github.com/05bit/peewee-async
[peewee]: https://github.com/coleifer/peewee
[motor]: https://github.com/mongodb/motor
[aioelasticsearch]: https://github.com/aio-libs/aioelasticsearch
[aioredis]: https://github.com/aio-libs/aioredis
[tortoise-db-backends]: https://tortoise-orm.readthedocs.io/en/latest/index.html#pluggable-database-backends
[tortoise-setup]: https://tortoise-orm.readthedocs.io/en/latest/setup.html
[events]: ../../guides/agnostic/events.md
[tortoise-getting-started]: https://tortoise-orm.readthedocs.io/en/latest/getting_started.html
[bloguero]: https://github.com/bocadilloproject/bloguero
