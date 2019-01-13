# Databases

Storing data and/or retrieving it from a database is a very common task to perform in a server-side web application. This page will discuss some aspects of how you can work with databases in Bocadillo, and what to expect in the future.

## How can Bocadillo help me work with a database?

**Bocadillo does not currently provide its own database layer.** It is however an important feature which we would like to support in a mid-term future.

This means that, in the meantime, you'll need to integrate with third-party libraries.

::: tip
You may find some features built into Bocadillo handy when integrating a third-party database library.

One of them is [event handlers][event-handlers], which can typically allow you to initialize and clean up database connections.
:::

In the rest of this document, we'll go through third-party solutions that you may find useful for a range of use cases.

::: warning Do I have do use async?

We recommend you do because **making queries to a database is typically I/O-bound** and represents most of the processing time in a typical server-side web application.

Using a synchronous client or ORM such as [SQLAlchemy] will make the server block while it is waiting for results, annihilating performance gains you obtained from using an asynchronous web framework like Bocadillo.

Because of this, we'll only discuss async solutions here.
:::

## NoSQL

If you're using a NoSQL database, many high-quality async clients are already available. Some examples are:

- [Motor] for MongoDB.
- [aioelasticsearch] for ElasticSearch.
- [aioredis] for Redis.

## SQL

### Use a database client

Depending on your use case, you may not need to resort to a full-blown ORM. In that case, you may get away with using a database-specific async SQL client, such as:

- [asyncpg] for PostgreSQL.
- [aiomysql] for MySQL.
- [aiosqlite] for SQLite.

### Use an ORM

#### What is an ORM?

Paraphrasing the [Wikipedia page][orm-wikipedia], ORM — a.k.a. *Object Relational Mapping* — is a programming technique to convert data between incompatible type systems.

Although it is a general concept, *an ORM* typically refers to software that acts as **a conversion layer between a given programming language and a database**, e.g. between Python and PostgreSQL.

Put simply, an ORM allows the developer to interact with the database through objects and method calls instead of writing SQL queries by hand.

#### Do I need an ORM?

Using an ORM has the benefit of making the data manipulation code more reusable, more consistent and more secure.

That said, keep in mind that ORMs have downsides, too. [Full Stack Python's article on Object Relation Mappers][fsp-article] mentions impedance mismatch, potentially reduced performance, and shift of complexity from the database to application code.

If this is too much for you, consider resorting to an [async SQL client](#use-a-database-client) instead.

#### Which async ORMs are available?

The world of asynchronous Python ORMs is still maturing. There, however, a few solutions available already.

A first approach is to use an **async ORM built on top of a synchronous one**. Examples include [GINO][gino] (built on SQLAlchemy Core) or [peewee-async] (built on [peewee]). This has the advantage of exposing an API familiar to the sync equivalent. But these may have extra performance overhead and missing features because of incompatibilities with the asynchronous paradigm.

Another approach is to use an **async-first ORM**. Few of them exist, but the most promising seems to be [Tortoise ORM][tortoise]. It is a from-scratch ORM implementation specifically targeted at async Python applications, which exposes a clean API very reminiscent of the Django ORM.

::: tip
We discuss how to integrate Tortoise ORM in a Bocadillo application in our how-to guide: [Use Tortoise ORM to interact with an SQL database][tortoise-how-to].
:::

[orm-wikipedia]: https://en.wikipedia.org/wiki/Object-relational_mapping
[fsp-article]: https://www.fullstackpython.com/object-relational-mappers-orms.html
[sqlalchemy]: https://www.sqlalchemy.org
[asyncpg]: https://www.github.com/MagicStack/asyncpg
[aiomysql]: https://github.com/aio-libs/aiomysql
[aiosqlite]: https://github.com/jreese/aiosqlite
[gino]: https://github.com/fantix/gino
[peewee-async]: https://github.com/05bit/peewee-async
[peewee]: https://github.com/coleifer/peewee
[motor]: https://github.com/mongodb/motor
[aioelasticsearch]: https://github.com/aio-libs/aioelasticsearch
[aioredis]: https://github.com/aio-libs/aioredis
[event-handlers]: ../guides/agnostic/events.md
[tortoise]: https://tortoise-orm.readthedocs.io
[tortoise-how-to]: ../how-to/tortoise.md
